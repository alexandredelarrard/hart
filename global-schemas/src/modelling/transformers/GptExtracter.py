import os
import json
from pathlib import Path
from os.path import dirname, abspath

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_vertexai import ChatVertexAI
from google.oauth2.credentials import Credentials
from pydantic import ValidationError
import vertexai

from omegaconf import DictConfig
from src.context import Context
from src.utils.step import Step


class GptExtracter(Step):

    def __init__(
        self,
        context: Context,
        config: DictConfig,
    ):

        super().__init__(context=context, config=config)

        self.seed = self._config.gpt.seed
        self.llm_model = self._config.gpt.llm_model
        self.prompt_path = dirname(dirname(abspath(__file__))) / Path(
            "prompt_templates"
        )

        self.get_api_keys()

    def read_prompts(self, user_prompt):

        # prompt template
        self.system_prompt = self.read_prompt_file(
            self.prompt_path / Path(f"{self._config.gpt.llm_action}_system_prompt.md")
        )
        self.user_prompt = self.read_prompt_file(
            self.prompt_path / Path(f"{user_prompt}_prompt.md")
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

    def create_prompt(self, schema):

        prompt = PromptTemplate(
            template=self.system_prompt + "\n" + self.user_prompt,
            input_variables=["query"],
            partial_variables={"_format": self.parser.get_format_instructions()},
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

    def invoke_llm(self, llm_input, chain):
        message_content = chain.invoke({"query": llm_input})
        try:
            message_content = json.loads(message_content.json())
            return message_content
        except json.JSONDecodeError as e:
            self._log.error(f"Error decoding JSON: {e}")
            return None
        except ValidationError as e:
            self._log.error(f"Validation error: {e}")
            return None

    def get_answer(self, llm_input, chain):

        message_content = self.invoke_llm(llm_input, chain)

        if not message_content:
            query_status = 400
        else:
            query_status = 200
            self._log.info(message_content)

        return message_content, query_status
