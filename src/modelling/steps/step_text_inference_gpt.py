import openai
import glob
import time
import pandas as pd 
from queue import Queue
from threading import Thread

from tqdm import tqdm 
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
                threads : int = 6):

        super().__init__(context=context, config=config)

        self.client = openai.OpenAI()
        self.seed = self._config.gpt.seed
        self.llm_model = self._config.gpt.llm_model
        self.threads = threads
        self.save_in_queue = True
        self.save_queue_size_step = 50
        self.save_queue_path= self._config.gpt.save_path

        self.queues = {"descriptions" : Queue(), "results": Queue()}

    @timing
    def run(self):

        # get data
        df = pd.read_sql("V2_WATCH_PREDICTION_030424", con=self._context.db_con)
        df = df.loc[df["PROBA_0"] >= 0.9]

        # get already done 
        df_done = read_crawled_pickles(path=self.save_queue_path)
        if df_done.shape[0] !=0:
            id_done = df_done[self.name.id_item].tolist()
            df = df.loc[~df[self.name.id_item].isin(id_done)]

        # initalize the urls queue
        self.initialize_queue_description(df, 
                                          category="watch")
        
        # start the crawl
        self.start_threads_and_queues(queues=self.queues)

        # multithread gpt queries
        t0 = time.time()
        self.queues["descriptions"].join()
        self._log.info('*** Done in {0}'.format(time.time() - t0))


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

            try:
                prompt = queue_desc.get()
                prompt["ANSWER"] = self.get_answer(prompt[self.name.total_description])

                if self.save_in_queue:
                    queues["results"].put(prompt)

                    if queues["results"].qsize() == self.save_queue_size_step:
                        file_name = encode_file_name(prompt[self.name.id_item])
                        save_queue_to_file(queues["results"], 
                                            path=self.save_queue_path +
                                            f"/{file_name}.pickle")
                
                queue_desc.task_done()
                self._log.info(f"[OOF {queue_desc.qsize()}] QUERIED {prompt[self.name.id_item]}")

            except Exception as e:
                self._log.error(f"Could not retreive desc - {e}")

        # last saving
        file_name = encode_file_name(prompt[self.name.id_item])
        save_queue_to_file(queues["results"], 
                                path=self.save_queue_path +
                                f"/{file_name}.pickle")

        
    def create_prompt(self, text : str, category : str):
        prompt = {"role": "user", 
                 "content": """prompt: Extract information from the %s description with a json format used for data analysis.
                               text: '%s' """%(category, text)}
        return prompt

    def get_answer(self, prompt):

        stream = self.client.chat.completions.create(
            model=self.llm_model,
            seed=self.seed,
            messages=[prompt],
            temperature=0,
            stream=False,       
        )
        message_content = stream.choices[0].message.content
        return message_content

    def clean_answers(self, answers):

        final = []
        for answer in answers:
            final.append(eval(answer.replace("\"\"", "\"")))

        return pd.DataFrame(final)

# schema : {
#         "category": "watch",
#         "house": str,
#         "gender" : str,
#         "watch name" : str,
#         "period or year": str,
#         "bracelet material": str,
#         "case material": str,
#         "case shape": str,
#         "cadran material": str,
#         "number complications" : int,
#         "type of movement":  str,
#         "object condition": str,
#         "box available": Bool,
#         "certificate available" : Bool,
#         "weight" : float,
#         "%s diameter" : float,
#     }