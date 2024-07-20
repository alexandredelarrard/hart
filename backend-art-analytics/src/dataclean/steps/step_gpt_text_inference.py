import os
import time
import ast
from queue import Queue
from typing import List
from threading import Thread
from pathlib import Path

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_vertexai import ChatVertexAI
from google.oauth2.credentials import Credentials
import vertexai

from omegaconf import DictConfig
from src.schemas.gpt_schemas import get_mapping_pydentic_object

from src.utils.utils_crawler import (
    encode_file_name,
    read_crawled_pickles,
    save_queue_to_file,
)

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing


class StepTextInferenceGpt(Step):

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

        self.seed = self._config.gpt.seed
        self.llm_model = self._config.gpt.llm_model
        self.save_queue_path = "/".join([self._config.gpt.save_path, self.object])

        self.save_in_queue = True
        self.queues = {"descriptions": Queue(), "results": Queue(), "clients": Queue()}
        self.get_api_keys()

    @timing
    def run(self):

        # get data DONE: moderne, figuratif
        # df = self.read_sql_data(f"SELECT * FROM \"PICTURES_CATEGORY_07_06_2024_286\" WHERE \"TOP_0\" in ('bijou bague')")
        df = self.read_sql_data(
            f'SELECT "ID_ITEM", "ITEM_TITLE_DETAIL", "TOTAL_DESCRIPTION" FROM "ALL_ITEMS_per_item"'
        )
        # df = df.merge(df_desc, on="ID_UNIQUE", how="left")
        df = df.drop_duplicates(self.name.total_description).fillna("")
        df = df.sample(frac=1).reset_index(drop=True)

        # get already done
        df_done = read_crawled_pickles(path=self.save_queue_path)
        if df_done.shape[0] != 0:
            id_done = df_done[self.name.id_item].tolist()
            df = df.loc[~df[self.name.id_item].isin(id_done)]

        # read prompts
        self.read_prompts()

        # get parser
        self.schema = get_mapping_pydentic_object(self.object)
        self.parser = PydanticOutputParser(pydantic_object=self.schema)
        self.prompt = self.create_prompt()

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

    def read_prompts(self):

        # prompt template
        self.system_prompt = self.read_prompt_file(
            Path(self._config.gpt.prompt_path)
            / f"{self._config.gpt.llm_action}_system_prompt.md"
        )
        self.user_prompt = self.read_prompt_file(
            Path(self._config.gpt.prompt_path) / f"{self.object}_prompt.md"
        )

    def initialize_client(self, methode):
        if methode == "open_ai":
            client = self.initialize_client_open_ai()
        elif methode == "groq":
            client = self.initialize_client_groq()
        elif methode == "local":
            client = self.initialize_client_local()
        elif methode == "google":
            client = self.initialize_client_google()
        else:
            raise Exception("Please provide a method either in open_ai, groq or local")
        self._log.info(f"INITIALIZED CLIENT {methode}")
        return client

    def get_api_keys(self):
        self.api_keys = {"openai": [], "groq": [], "google": []}
        self.api_keys_index = {"openai": 0, "groq": 0, "google": 0}
        for key, item in os.environ.items():
            if "OPENAI_API_KEY" in key:
                self.api_keys["openai"].append(item)
            if "GROQ_API_KEY" in key:
                self.api_keys["groq"].append(item)
            if "GOOGLE_API_KEY" in key:
                self.api_keys["google"].append(item)

        if len(self.api_keys) == 0:
            raise Exception("Please provide an API KEY in .env file for OPENAI")

    def initialize_client_open_ai(self):
        self.api_keys_index["openai"] = (self.api_keys_index["openai"] + 1) % len(
            self.api_keys["openai"]
        )
        client = ChatOpenAI(
            openai_api_key=self.api_keys["openai"][self.api_keys_index["openai"]],
            model=self.llm_model["open_ai"],
            model_kwargs={"response_format": {"type": "json_object"}},
            temperature=0.2,
        )
        self._log.info(f"OPEN API_KEY INDEX {self.api_keys_index['openai']}")
        return client

    def initialize_client_local(self):
        client = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            openai_api_key="lm-studio",
            model=self.llm_model["local"],
            model_kwargs={"response_format": {"type": "json_object"}},
            temperature=0.2,
        )
        return client

    def initialize_client_groq(self):
        client = ChatGroq(
            groq_api_key=self.api_keys["groq"][0],
            model=self.llm_model["groq"],
            temperature=0.2,
            max_tokens=4096,
        )
        return client

    def initialize_client_google(self):
        creds = Credentials.from_authorized_user_file(
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"], []
        )
        vertexai.init(
            project=creds.quota_project_id, location="europe-west1", credentials=creds
        )
        client = ChatVertexAI(
            credentials=creds,
            model=self.llm_model["google"],
            responseMimeType="application/json",
            responseSchema=self.parser,
            temperature=0.2,
            max_tokens=4096,
            location="europe-west1",
            seed=self.seed,
        )
        return client

    def initialize_queue_description(self, df):
        for row in df.to_dict(orient="records"):
            item = {
                self.name.id_item: row[self.name.id_item],
                self.name.total_description: row[self.name.detailed_title].lower()
                + "\n "
                + row[self.name.total_description],
            }
            self.queues["descriptions"].put(item)

    def create_prompt(self):
        prompt = PromptTemplate(
            template=self.system_prompt + self.user_prompt,
            input_variables=["query"],
            partial_variables={"_format": self.schema.schema_json()},
        )
        return prompt

    def read_prompt_file(self, path: Path) -> str:
        """Get the content of a file as a string.

        Args:
            path (Path): The path to the file.

        Raises:
            FileNotFoundError: If the file does not exist or is a directory

        Returns:
            str: The content of the file
        """
        if os.path.isdir(path):
            raise FileNotFoundError(
                f"Provided path {str(path)} is a directory, not a file"
            )
        if os.path.exists(path):
            with open(path, "r") as fp:
                return fp.read()

        raise FileNotFoundError(f"Missing file {path} in path {str(path)}")

    def invoke_llm(self, prompt, chain):
        message_content = chain.invoke({"query": prompt[self.name.total_description]})
        try:
            message_content = ast.literal_eval(message_content.json())
        except Exception:
            pass
        return message_content

    def get_answer(self, prompt, chain):

        message_content = ""
        try:
            message_content = self.invoke_llm(prompt, chain)
            query_status = "200"
            self._log.info(message_content)
        except Exception as e:
            self._log.error(e)
            query_status = "400"

        return message_content, query_status

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
            prompt = queue_desc.get()

            prompt["ANSWER"], query_status = self.get_answer(prompt, chain)
            prompt["METHODE"] = chain.to_json()["kwargs"]["middle"][0].__module__

            if query_status != "200":
                # queues["descriptions"].put(prompt)
                self._log.critical(f"Error for {prompt[self.name.id_item]}")

            if self.save_in_queue and query_status == "200":
                queues["results"].put(prompt)
                queue_desc.task_done()

                if queues["results"].qsize() == self.save_queue_size_step:
                    file_name = encode_file_name(prompt[self.name.id_item])
                    save_queue_to_file(
                        queues["results"],
                        path=self.save_queue_path + f"/{file_name}.pickle",
                    )

            # done task
            queues["clients"].put(chain)
            self._log.info(
                f"[OOF {queue_desc.qsize()}] QUERIED {prompt[self.name.id_item]}"
            )

            # last saving
            if queues["descriptions"].qsize() == 0:
                file_name = encode_file_name(prompt[self.name.id_item])
                save_queue_to_file(
                    queues["results"],
                    path=self.save_queue_path + f"/{file_name}.pickle",
                )
