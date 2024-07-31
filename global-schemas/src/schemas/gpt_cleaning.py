from pydantic import Field
from src.schemas.gpt_schemas import Reformulate


class GptTranslateCategorize(Reformulate):
    __tablename__ = "GPT_TRANSLATE_CATEGORIZE"
    __table_args__ = {"extend_existing": True}

    id_item: str = Field(description="unique id item")
    input: str = Field(description="Item description")
    date_run: str = Field(description="When the LLM was triggered")
    clean_object_category: str = Field(
        description="cleaned category found from object category LLM"
    )
