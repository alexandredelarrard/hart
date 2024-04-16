import openai
openai.api_version = "2023-07-01-preview"
import os
import time
from queue import Queue
import phoenix as px
from threading import Thread

from omegaconf import DictConfig
from src.schemas.gpt_schemas import Vase
from src.genai_utils.traced_calls import TracedVLLMCompletion
from src.genai_utils.params import vLLMExtraCompletionParams

from src.utils.utils_crawler import (encode_file_name,
                                     read_crawled_pickles,
                                     save_queue_to_file)
from src.utils.utils_dataframe import (remove_accents,
                                       remove_punctuation)
from src.genai_utils.tracing import (maybe_load_trace_dataset,
                                    is_phoenix_already_launched,
                                    save_trace_dataset)
from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing


class StepTextInferenceGpt(Step):

    def __init__(self, 
                context : Context,
                config : DictConfig,
                object : str,
                threads : int = 7,
                save_queue_size : int = 50):

        super().__init__(context=context, config=config)

        self.save_queue_size_step = save_queue_size
        self.threads = threads
        self.object = object

        self.seed = self._config.gpt.seed
        self.llm_model = self._config.gpt.llm_model
        self.save_queue_path= self._config.gpt.save_path
        self.prompts_schema = self._config.gpt.prompts_schema

        self.save_in_queue = True
        self.queues = {"descriptions" : Queue(), "results": Queue()}
        self.get_api_keys()


    @timing
    def run(self):

        # initialize tracking in localhos:6006
        self.initialize_phoenix()

        # initialize client OPENAI
        self.initialize_client(api_keys=self.api_keys)
        
        # get data
        # df = pd.read_sql("TEST_0.05_06_04_2024", con=self._context.db_con)
        # df = df.loc[df["PROBA_0"] >= 0.85]
        # df = df.loc[df["TOP_0"] == self.object]
        df = self.read_sql_data(self._config.cleaning.full_data_auction_houses) 
        df = df.loc[df[self.name.total_description].apply(lambda x: " vase " in " " + str(x).lower() + " ")].sample(frac=0.25)
        df = df.drop_duplicates(self.name.total_description)
        df = df.loc[df[self.name.total_description].str.len() > 60] # minimal desc size to have
        df = df.loc[df[self.name.eur_item_result]> 5]

        # get already done 
        df_done = read_crawled_pickles(path=self.save_queue_path)
        if df_done.shape[0] !=0:
            id_done = df_done[self.name.id_item].tolist()
            df = df.loc[~df[self.name.id_item].isin(id_done)]
        df = df.sample(frac=1)

        # initalize the urls queue
        self.initialize_queue_description(df, category=self.object)
        
        # start the crawl
        self.start_threads_and_queues(queues=self.queues)

        # multithread gpt queries
        t0 = time.time()
        self.queues["descriptions"].join()
        self._log.info('*** Done in {0}'.format(time.time() - t0))
        

    def initialize_queue_description(self, df, category):
        for row in df.to_dict(orient="records"):
            item = {self.name.id_item : row[self.name.id_item],
                    self.name.prompt_description : self.create_prompt(row[self.name.total_description], 
                                                                     category),
                    self.name.category: category.upper(),
                    self.name.total_description: row[self.name.total_description]}

            self.queues["descriptions"].put(item)

    def start_threads_and_queues(self, queues):

        for _ in range(self.threads):
            t = Thread(target= self.queue_gpt, args=(queues, )) 
            t.daemon = True
            t.start()
        
    def queue_gpt(self, queues):

        queue_desc = queues["descriptions"]

        while True:
            prompt = queue_desc.get()
            prompt["ANSWER"], query_status = self.get_answer(prompt)

            if query_status != "200":
                if len(self.api_keys) > 1:
                    self.api_keys = self.api_keys[1:]
                    self.initialize_client(self.api_keys)
                else:
                    self._log.critical(f"NO API KEY AVAILABLE STOP CRAWLING GPT | current {self.client.api_key}")
                    break

            if self.save_in_queue:
                queues["results"].put(prompt)

                if queues["results"].qsize() == self.save_queue_size_step:
                    file_name = encode_file_name(prompt[self.name.id_item])
                    save_queue_to_file(queues["results"], 
                                        path=self.save_queue_path +
                                        f"/{file_name}.pickle")
            
            # done task
            queue_desc.task_done()
            self._log.info(f"[OOF {queue_desc.qsize()}] QUERIED {prompt[self.name.id_item]}")

            # last saving
            if queues["descriptions"].qsize() == 0:
                file_name = encode_file_name(prompt[self.name.id_item])
                save_queue_to_file(queues["results"], 
                                        path=self.save_queue_path +
                                        f"/{file_name}.pickle")

    def create_prompt(self, text : str, category: str):

        text = remove_punctuation(remove_accents(text)).lower().strip()
        schema= str(self.prompts_schema[category]).replace("\n", "")

        prompt = {"role": "user", 
                 "content": """You are an art expert of %s. Extract caracteristics from the description. Give a JSON format with values in english. List of JSON if several %ss. Only render found information.
                 List: %s
                 description: %s"""%(category, category, schema, text)}
        
        return prompt

    def get_answer(self, prompt):

        message_content= ""
        messages = []

        try:
            #step 1
            stream = self.client.chat.completions.create(
                model=self.llm_model,
                seed=self.seed,
                messages=[{"role": "user", 
                           "content": "Art Description : " + prompt[self.name.total_description]}],
                temperature=0,
                stream=False,       
            )
            message_content = self.get_text(stream)
            messages.append({"role": "assistant", "content": message_content})
            messages.append(prompt[self.name.prompt_description])

            # step2
            stream = self.client.chat.completions.create(
                model=self.llm_model,
                seed=self.seed,
                messages=messages,
                temperature=0,
                response_format={"type": "json_object"},
                stream=False,       
            )
            
            message_content = self.get_text(stream)
            query_status = "200"

        except openai.APIError as e:
            #Handle API error here, e.g. retry or log
            self._log.error(f"OpenAI API returned an API Error: {e} / {e.code}")
            query_status = e.code
            pass

        except openai.APIConnectionError as e:
            #Handle connection error here
            self._log.error(f"Failed to connect to OpenAI API: {e}")
            query_status = e.code
            pass

        except openai.RateLimitError as e:
            #Handle rate limit error (we recommend using exponential backoff)
            self._log.error(f"OpenAI API request exceeded rate limit: {e}")
            query_status = e.status_code
            pass

        return message_content, query_status
    
    def get_text(self, stream):
        return stream.choices[0].message.content
    
    def get_api_keys(self):
        self.api_keys = []
        for key, item in os.environ.items():
            if "OPENAI_API_KEY" in key: 
                self.api_keys.append(item)
        
        if len(self.api_keys) == 0:
            raise Exception("Please provide an API KEY in .env file for OPENAI")

    def initialize_client(self, api_keys):
        self.client = openai.OpenAI(api_key=api_keys[0])
        self._log.info(f"Run with API key : {self.client.api_key}")

    def initialize_phoenix(self):
        if not is_phoenix_already_launched():
            tds = maybe_load_trace_dataset(trace_dir="D:/data/llm_log/")
            self.px_session = px.launch_app(trace=tds)
        else:
            self._log.info("Phoenix already launched at http://localhost:6006")
        
        try:
            save_trace_dataset(px.Client(), trace_dir="D:/data/llm_log/")
        except Exception:
            pass

    def initialize_llm(self, schema):
        format = vLLMExtraCompletionParams(response_format=Vase.model_json_schema())
        self.llm = TracedVLLMCompletion(client = self.client,
                                        # vllm_extra_completion_params=format,
                                        openai_completion_params={
                                            "model":self.llm_model,
                                            "seed":self.seed,
                                            "temperature":0})
