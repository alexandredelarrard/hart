import openai
import os
import time
import pandas as pd 
from queue import Queue
from threading import Thread

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from omegaconf import DictConfig
from src.utils.utils_crawler import (encode_file_name,
                                     read_crawled_pickles,
                                     save_queue_to_file)


class StepTextInferenceGpt(Step):

    def __init__(self, 
                context : Context,
                config : DictConfig,
                threads : int = 7,
                save_queue_size : int = 50):

        super().__init__(context=context, config=config)

        
        self.seed = self._config.gpt.seed
        self.llm_model = self._config.gpt.llm_model
        self.threads = threads
        self.save_in_queue = True
        self.save_queue_size_step = save_queue_size
        self.save_queue_path= self._config.gpt.save_path

        self.queues = {"descriptions" : Queue(), "results": Queue()}
        self.get_api_keys()


    @timing
    def run(self):

        self.initialize_client(api_keys=self.api_keys)

        # get data
        df = pd.read_sql("V2_WATCH_PREDICTION_030424", con=self._context.db_con)
        df = df.loc[df["PROBA_0"] >= 0.9]
        df = df.drop_duplicates(self.name.total_description)
        df = df.sample(frac=1)

        # get already done 
        df_done = read_crawled_pickles(path=self.save_queue_path)
        if df_done.shape[0] !=0:
            id_done = df_done[self.name.id_item].tolist()
            df = df.loc[~df[self.name.id_item].isin(id_done)]

        # initalize the urls queue
        self.initialize_queue_description(df, category="watch")
        
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
        self.client = openai.OpenAI(api_key=api_keys[0])
        self._log.info(f"Run with API key : {self.client.api_key}")

    def initialize_queue_description(self, df, category):
        for row in df.to_dict(orient="records"):
            item = {self.name.id_item : row[self.name.id_item],
                    self.name.total_description : self.create_prompt(row[self.name.total_description], 
                                                                     category)}

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
            prompt["ANSWER"], query_status = self.get_answer(prompt[self.name.total_description])

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
        prompt = {"role": "user", 
                 "content": """Extract caracteristics from the watch description following the List format. Give a JSON format with values in english. List of JSON if several watches. Only render found information.
                 List: {"watch_brand": str, "watch_category": str, "watch_model_or_collection_name": str, "watch_movement": str, "gender" : str, "watch_circa_year_or_period": str, "dial_material": str, "dial_color": str, "dial_luminous":bool, "case_or_dial_shape": str,  "case_material": str,  "case_size": str, "watch_reference": str, "bracelet_or_strap_material": str, "number_jewels": int, "jewels_type": str, "bracelet_or_strap_color": str, "dial_or_case_diameter": str,  "watch_weight": str,  "watch_serial_number": str,  "buckle_or_clasp": str, "buckle_or_clasp_type": str, "dial_signature": str, "case_signature": str, "hour_marker_style": str, "minute_index_style": str, "hands_material": str, "hands_style": str, "is_date_displayed": bool,  "crystal_condition": str, "watch_functionning": bool, "limited_edition": str,  "water_resistant": bool, "has_certificate": bool, "is_certified": bool,  "has_chronometer_chronograph": bool, "number_subdial": int, "has_package_box": bool, "under_warranty": bool, "type_of_jewels": str, "number_carats": str, "case_back": str, "bracelet_length": str, "watch_condition": str, "crown_material": str, "glass_material": str, "has_moon_phase": str}
                 description: %s"""%(text)}
        return prompt

    def get_answer(self, prompt):

        message_content= ""
        try:
            stream = self.client.chat.completions.create(
                model=self.llm_model,
                seed=self.seed,
                messages=[prompt],
                temperature=0,
                stream=False,       
            )
            message_content = stream.choices[0].message.content
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
