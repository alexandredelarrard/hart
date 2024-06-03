import os
import time
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory 

from omegaconf import DictConfig
from src.context import Context
from src.utils.step import Step

class GptChat(Step):

    def __init__(self, 
                context : Context,
                config : DictConfig,
                methode: str ="open_ai"):

        super().__init__(context=context, config=config)

        self.methode = methode
        self.ai_prefix = "bot"
        self.seed = self._config.gpt.seed
        self.llm_model = self._config.gpt.llm_model[methode]
        self.introduction = self._config.gpt.introduction
        self.get_api_keys()

        # initialize chatbot
        self.client = self.initialize_client()
        self.prompt = self.create_prompt()
        self.chain = ConversationChain(llm=self.client,
                                        verbose=True, 
                                        combine_docs_chain_kwargs={"prompt": self.prompt}) 

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
        if self.methode in ["open_ai", "local"]:
            prompt = self.create_prompt_openai()
        else:
            raise Exception("eitjer open_ai or local to have a chat answer")
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
                            model=self.llm_model,
                            temperature=0.2,
                            seed=self.seed) 
        self._log.info(f"Run with API key : {client.openai_api_key}")
        return client
    
    def initialize_client_local(self):
        client = ChatOpenAI(base_url="http://localhost:1234/v1", 
                            openai_api_key="lm-studio",
                            model=self.llm_model,
                            temperature=0.2,
                            seed=self.seed) 
        self._log.info(f"Run with API key : {client.openai_api_key}")
        return client
    
    def initialize_client_groq(self):
        client = ChatGroq(groq_api_key=self.api_keys["groq"][0],
                        model=self.llm_model,
                        temperature=0,
                        max_tokens=512,
                        seed=self.seed) 
        self._log.info(f"Run with API key : {client.groq_api_key}")
        return client
    
    def create_prompt_openai(self):
        prompt = PromptTemplate(
            template=self.introduction + """
                        Close art piece description:
                        {art_pieces}
                        user: {question}
                        %s:"""%(self.ai_prefix),
            input_variables=["art_pieces", "question"],
        )
        return prompt
    
    def invoke_llm(self, art_pieces, question):
        if self.methode == "open_ai":
            message_content = self.chain.predict(art_pieces=art_pieces, question= question)
            print(message_content)
            # message_content = message_content.content
        else:
            raise Exception(f"wrong methode {self.methode}")
        return message_content

    def get_answer(self, art_pieces, question):
        
        message_content = ""
        try:
            message_content = self.invoke_llm(art_pieces, question)
            query_status = "200"
            self._log.info(message_content)
        except Exception as e:
            self._log.error(e)
            query_status = "400"

        return message_content, query_status
    