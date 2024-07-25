import time
from queue import Queue
from typing import List
from threading import Thread

from langchain_core.output_parsers import PydanticOutputParser
from omegaconf import DictConfig
from src.schemas.gpt_schemas import get_mapping_pydentic_object
from src.modelling.transformers.GptExtracter import GptExtracter
from src.utils.dataset_retreival import DatasetRetreiver

from src.schemas.gpt_schemas import LlmExtraction, ColName
from src.context import Context
from src.utils.timing import timing


class StepTextInferenceGpt(GptExtracter):

    def __init__(
        self,
        context: Context,
        config: DictConfig,
        threads: int = 1,
        object: str = "painting",
        methode: List[str] = ["open_ai"],
    ):

        super().__init__(context=context, config=config)

        self.threads = threads
        self.object = object
        self.methode = methode

        self.data_retreiver = DatasetRetreiver(context=context, config=config)
        self.sql_gpt_table_raw = LlmExtraction.__tablename__

        self.queues = {"descriptions": Queue(), "results": Queue(), "clients": Queue()}

    @timing
    def run(self):

        if self.object == "reformulate":
            df = self.data_retreiver.get_gpt_category_input()
        else:
            df = self.data_retreiver.get_gpt_object_extract_input(
                object_value=self.object, schema_prompt_value=self.object
            )
        self._log.info(f"GETTING {df.shape}")

        # read prompts
        self.read_prompts(user_prompt=self.object)

        # get parser
        self.schema = get_mapping_pydentic_object(self.object)
        self.parser = PydanticOutputParser(pydantic_object=self.schema)
        self.prompt = self.create_prompt(schema=self.schema)

        # initialize queue clients
        self.initialize_queue_clients()

        # initalize the urls queue
        self.initialize_queue_description(df)

        # start the crawl
        self.start_threads_and_queues(queues=self.queues)

        # multithread gpt queries
        t0 = time.time()
        self.queues["descriptions"].join()
        self._log.info("*** Done in {0}".format(time.time() - t0))

    def initialize_queue_description(self, df):
        for row in df.to_dict(orient="records"):

            # each input will be the concat of
            # all columns avialable except id_item
            input_string = ""
            for key, value in row.items():
                if key != ColName.id_item:
                    input_string += f"{key} : {value} \n"

            # create futur response
            new_response = LlmExtraction(
                id_item=row[ColName.id_item],
                input=input_string,
                prompt_schema=self.object,
            )

            self.queues["descriptions"].put(new_response)

    def start_threads_and_queues(self, queues):

        for _ in range(self.threads):
            t = Thread(target=self.queue_gpt, args=(queues,))
            t.daemon = True
            t.start()

    def initialize_queue_clients(self):
        for methode in self.methode:
            client = self.initialize_client(methode)
            self.queues["clients"].put(self.prompt | client | self.parser)

        if self.threads > len(self.methode):
            remaining = self.threads - len(self.methode)
            for i in range(remaining):
                self.queues["clients"].put(
                    self.prompt | self.initialize_client("open_ai") | self.parser
                )

    def queue_gpt(self, queues):

        queue_desc = queues["descriptions"]
        chain = queues["clients"].get()

        while True:

            # get the input from queue
            new_response = queue_desc.get()

            # get llm answer
            answer, query_status = self.get_answer(new_response.input, chain)

            if query_status == 400:
                self._log.critical(f"Error for {new_response.id_item}")

            else:
                # compleat the answer / response for db
                new_response.methode = chain.to_json()["kwargs"]["middle"][0].__module__
                new_response.answer = answer.dict()

                # save in db
                self.insert_raw_to_table(
                    unique_id_col="id_item",
                    row_dict=new_response.dict(),
                    table_name=self.sql_gpt_table_raw,
                )
                self._log.info(
                    f"[OOF {queue_desc.qsize()}] QUERIED {new_response.id_item}"
                )

            # done task
            queues["clients"].put(chain)
