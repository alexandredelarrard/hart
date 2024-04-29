import os
import time
from queue import Queue
import phoenix as px
from threading import Thread

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

from omegaconf import DictConfig
from src.schemas.gpt_schemas import get_mapping_pydentic_object

from src.utils.utils_crawler import (encode_file_name,
                                     read_crawled_pickles,
                                     save_queue_to_file)
from src.utils_genai.tracing import (maybe_load_trace_dataset,
                                    is_phoenix_already_launched,
                                    save_trace_dataset)
from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing


class StepTextInferenceGpt(Step):

    def __init__(self, 
                context : Context,
                config : DictConfig,
                threads : int = 1,
                object : str = "painting",
                save_queue_size : int = 50):

        super().__init__(context=context, config=config)

        self.save_queue_size_step = save_queue_size
        self.threads = threads
        self.object = object

        self.seed = self._config.gpt.seed
        self.llm_model = self._config.gpt.llm_model
        self.save_queue_path= self._config.gpt.save_path
        self.introduction = self._config.gpt.introduction

        self.save_in_queue = True
        self.queues = {"descriptions" : Queue(), "results": Queue()}
        self.get_api_keys()


    @timing
    def run(self):
        
        # get data
        df = self.read_sql_data(f"SELECT * FROM \"PICTURES_CATEGORY_20_04_2024\" WHERE \"TOP_0\"='tableau figuratif' AND \"PROBA_0\" > 0.9") #self._config.cleaning.full_data_auction_houses) 
        df = df.drop_duplicates(self.name.total_description)
        df = df.loc[df[self.name.total_description].str.len() > 100] # minimal desc size to have

        # get already done 
        df_done = read_crawled_pickles(path=self.save_queue_path)
        if df_done.shape[0] !=0:
            id_done = df_done[self.name.id_item].tolist()
            df = df.loc[~df[self.name.id_item].isin(id_done)]

        # get parser 
        pytendic_schemas = get_mapping_pydentic_object(self.object)
        self.client = self.initialize_client(api_keys=self.api_keys)
        self.parser = JsonOutputParser(pydantic_object=pytendic_schemas)
        self.prompt = self.create_prompt()
        self.chain = self.prompt | self.client | self.parser

        # initalize the urls queue
        self.initialize_queue_description(df)
        
        # start the crawl
        self.start_threads_and_queues(queues=self.queues)

        # multithread gpt queries
        t0 = time.time()
        self.queues["descriptions"].join()
        self._log.info('*** Done in {0}'.format(time.time() - t0))

    def get_api_keys(self):
        self.api_keys = []
        for key, item in os.environ.items():
            if "OPENAI_API_KEY" in key: 
                self.api_keys.append(item)
        
        if len(self.api_keys) == 0:
            raise Exception("Please provide an API KEY in .env file for OPENAI")

    def initialize_client(self, api_keys):
        client = ChatOpenAI(base_url="http://localhost:1234/v1", 
                            openai_api_key="lm-studio",
                            model=self.llm_model,
                            temperature=0,
                            seed=self.seed) 
        self._log.info(f"Run with API key : {client.openai_api_key}")
        return client

    def initialize_phoenix(self):
        if not is_phoenix_already_launched():
            tds = maybe_load_trace_dataset(trace_dir="D:/data/llm_log/")
            self.px_session = px.launch_app(trace=tds)
        else:
            self._log.info("Phoenix already launched at http://localhost:6006")
        
        save_trace_dataset(px.Client(), trace_dir="D:/data/llm_log/")

    def initialize_queue_description(self, df):
        for row in df.to_dict(orient="records"):
            item = {self.name.id_item: row[self.name.id_item],
                    self.name.total_description: row[self.name.total_description]}
            self.queues["descriptions"].put(item)
    
    def create_prompt(self):
        prompt = PromptTemplate(
            template=self.introduction + "\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
        return prompt

    def get_answer(self, prompt):
        
        message_content = ""
        try:
            message_content = self.chain.invoke({"query": "Description: " + prompt[self.name.total_description]})
            query_status = "200"

        except Exception as e:
            self._log.error(e)
            query_status = "400"

        return message_content, query_status

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
                self._log.critical(f"Error for {prompt[self.name.id_item]}")

            if self.save_in_queue and query_status == "200":
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

    

