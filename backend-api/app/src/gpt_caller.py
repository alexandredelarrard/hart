from typing import List, Any

from src.schemas.gpt_schemas import get_mapping_pydentic_object
from src.utils.step import Step
from src.modelling.transformers.GptExtracter import GptExtracter

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel
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

    def reshape_list_examples(self, examples: List[Any]):
        output_string = ""
        for i, example in enumerate(examples):
            output_string += f"Example {i}: " + str(example) + "\n\n"
        return output_string

    def get_llm_result(self, art_pieces):

        number_ex = 6
        steps = 3
        query_status = 400
        llm_results = {}

        while query_status != 200 and steps != 0:
            string_art_pieces = self.reshape_list_examples(art_pieces[:number_ex])

            llm_results, query_status = self.get_answer(
                llm_input=string_art_pieces, chain=self.chain
            )

            if isinstance(llm_results, BaseModel):
                llm_results = llm_results.dict()

            number_ex -= 2
            steps -= 1

        return llm_results
