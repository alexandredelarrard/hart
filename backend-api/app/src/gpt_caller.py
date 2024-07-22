from src.schemas.gpt_schemas import get_mapping_pydentic_object
from src.utils.step import Step
from src.modelling.transformers.GptExtracter import GptExtracter

from langchain_core.output_parsers import PydanticOutputParser
from src.context import Context

from omegaconf import DictConfig


class GptChat(GptExtracter):

    def __init__(self, context: Context, config: DictConfig, methode: str = "open_ai"):

        config.gpt.llm_action = "designate"
        super().__init__(context=context, config=config)

        self.seed = self._config.gpt.seed
        self.temperature = self._config.gpt.temperature
        self.get_api_keys()

        # read prompts
        self.read_prompts(user_prompt="designate")

        # initialize chatbot
        self.schema = get_mapping_pydentic_object("reformulate")
        self.parser = PydanticOutputParser(pydantic_object=self.schema)
        self.prompt = self.create_prompt(schema=self.schema)

        self.client = self.initialize_client(methode)
        self.chain = self.prompt | self.client | self.parser
