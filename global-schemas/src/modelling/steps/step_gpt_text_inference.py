import time
from queue import Queue
from typing import List
from threading import Thread
from pathlib import Path

from langchain_core.output_parsers import PydanticOutputParser
from omegaconf import DictConfig
from src.schemas.gpt_schemas import get_mapping_pydentic_object
from src.modelling.transformers.GptExtracter import GptExtracter

from src.utils.utils_crawler import (
    encode_file_name,
    read_crawled_pickles,
    save_queue_to_file,
)

from src.context import Context
from src.utils.timing import timing


class StepTextInferenceGpt(GptExtracter):

    def __init__(
        self,
        context: Context,
        config: DictConfig,
        threads: int = 1,
        object: str = "painting",
        save_queue_size: int = 50,
        methode: List[str] = ["open_ai"],
    ):

        super().__init__(context=context, config=config)

        self.save_queue_size_step = save_queue_size
        self.threads = threads
        self.object = object
        self.methode = methode

        self.save_queue_path = self._context.paths["LLM_EXTRACTED"] / Path(self.object)

        self.save_in_queue = True
        self.queues = {"descriptions": Queue(), "results": Queue(), "clients": Queue()}

    @timing
    def run(self):

        # todo
        df = self.read_sql_data(
            f'SELECT "ID_ITEM", "ITEM_TITLE_DETAIL", "TOTAL_DESCRIPTION" FROM "ALL_ITEMS_per_item"'
        )
        df = df.drop_duplicates(self.name.total_description).fillna("")
        df = df.sample(frac=1).reset_index(drop=True)

        # get already done
        df_done = read_crawled_pickles(path=self.save_queue_path)
        if df_done.shape[0] != 0:
            id_done = df_done[self.name.id_item].tolist()
            df = df.loc[~df[self.name.id_item].isin(id_done)]

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
            dict_inputs = queue_desc.get()
            llm_input = dict_inputs[self.name.total_description]

            dict_inputs["ANSWER"], query_status = self.get_answer(llm_input, chain)
            dict_inputs["METHODE"] = chain.to_json()["kwargs"]["middle"][0].__module__

            if query_status == 400:
                self._log.critical(f"Error for {dict_inputs[self.name.id_item]}")

            if self.save_in_queue and query_status == 200:
                queues["results"].put(dict_inputs)
                queue_desc.task_done()

                if queues["results"].qsize() == self.save_queue_size_step:
                    file_name = encode_file_name(dict_inputs[self.name.id_item])
                    save_queue_to_file(
                        queues["results"],
                        path=self.save_queue_path / Path(f"{file_name}.pickle"),
                    )

            # done task
            queues["clients"].put(chain)
            self._log.info(
                f"[OOF {queue_desc.qsize()}] QUERIED {dict_inputs[self.name.id_item]}"
            )

            # last saving
            if queues["descriptions"].qsize() == 0:
                file_name = encode_file_name(dict_inputs[self.name.id_item])
                save_queue_to_file(
                    queues["results"],
                    path=self.save_queue_path / Path(f"/{file_name}.pickle"),
                )
