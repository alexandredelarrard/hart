import os
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_vertexai import ChatVertexAI
from google.oauth2.credentials import Credentials
import vertexai

from omegaconf import DictConfig
from src.schemas.llm_schemas import get_mapping_pydentic_object
from src.context import Context
from src.utils.step import Step

SCOPES = ["https://www.googleapis.com/auth/contacts.readonly"]

class GptChat(Step):

    def __init__(self, 
                context : Context,
                config : DictConfig,
                methode: str ="open_ai"):

        super().__init__(context=context, config=config)

        self.methode = methode
        self.seed = self._config.gpt.seed
        self.llm_model = self._config.gpt.llm_model
        self.introduction = self._config.gpt.introduction["prod_designation"]
        self.temperature = self._config.gpt.temperature
        self.object = "designation"
        self.get_api_keys()

        # initialize chatbot
        self.schema = get_mapping_pydentic_object(self.object)
        self.parser = PydanticOutputParser(pydantic_object=self.schema)
        self.prompt = self.create_prompt()

        self.client = self.initialize_client()
        self.chain = self.prompt | self.client | self.parser

    def initialize_client(self):
        if self.methode == "open_ai":
            client = self.initialize_client_open_ai()
        elif self.methode == "groq":
            client = self.initialize_client_groq()
        elif self.methode == "local":
            client = self.initialize_client_local()
        else:
            raise Exception("Please provide a method either in open_ai, groq or local")
        return client
    
    def create_prompt(self):
        prompt = PromptTemplate(
            template=self.introduction + " \n JSON Instruction: {format_instructions} \n List of Descriptions : {query}",
            input_variables=["query"],
            partial_variables={"format_instructions": self.parser.get_format_instructions().replace("```", "")},
        )
        return prompt

    def get_api_keys(self):
        self.api_keys = {"openai": [], "groq": []}
        for key, item in os.environ.items():
            if "OPENAI_API_KEY" in key: 
                self.api_keys["openai"].append(item)
            if "GROQ_API_KEY" in key: 
                self.api_keys["groq"].append(item)
        
        if len(self.api_keys) == 0:
            raise Exception("Please provide an API KEY in .env file for OPENAI")

    def initialize_client_open_ai(self):
        client = ChatOpenAI(openai_api_key=self.api_keys["openai"][0],
                            model=self.llm_model["open_ai"],
                            model_kwargs={"response_format": {"type": "json_object"}},
                            temperature=0.2,
                            seed=self.seed) 
        return client
    
    def initialize_client_local(self):
        client = ChatOpenAI(base_url="http://localhost:1234/v1", 
                            openai_api_key="lm-studio",
                            model=self.llm_model["local"],
                            model_kwargs={"response_format": {"type": "json_object"}},
                            temperature=0.2,
                            seed=self.seed) 
        return client
    
    def initialize_client_groq(self):
        client = ChatGroq(groq_api_key=self.api_keys["groq"][0],
                        model=self.llm_model["groq"],
                        temperature=0.2,
                        max_tokens=2048,
                        seed=self.seed) 
        return client
    
    def initialize_client_google(self):
        creds = Credentials.from_authorized_user_file(os.environ["GOOGLE_APPLICATION_CREDENTIALS"], SCOPES)
        vertexai.init(project=creds.quota_project_id, location="europe-west1", credentials=creds)
        client = ChatVertexAI(
                            credentials=creds,
                            model=self.llm_model["google"],
                            responseMimeType='application/json',
                            responseSchema=self.parser,
                            temperature=0.2,
                            max_tokens=2048,
                            location="europe-west1",
                            seed=self.seed
                        )
        return client
    
    def invoke_llm(self, prompt):
        message_content = self.chain.invoke({"query": prompt})
        try:
            message_content = eval(message_content.json())
        except Exception:
            pass
        return message_content

    def get_answer(self, prompt):
        
        message_content = ""
        try:
            message_content = self.invoke_llm(prompt=prompt)
            query_status = 200
            self._log.info(message_content)
        except Exception as e:
            self._log.error(e)
            query_status = 400

        return message_content, query_status
    