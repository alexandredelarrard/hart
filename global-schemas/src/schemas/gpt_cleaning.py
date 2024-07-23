from langchain_core.pydantic_v1 import BaseModel, Field


class GptTranslateCategorize(BaseModel):
    __tablename__ = "GPT_TRANSLATE_CATEGORIZE"
    __table_args__ = {"extend_existing": True}

    ID_ITEM: str = Field("", description="unique id item")
    TOTAL_DESCRIPTION: str = Field("", description="Item description")
    METHODE: str = Field("", description="LLM methode used to extract json")
    FILE_CREATION_DATE: str = Field(
        "", description="Time when the extraction was done and saved"
    )
    FILE: str = Field("", description="File name saved on disk")
    OBJECT_CATEGORY: str = Field("", description="original category deduced from LLM")
    FRENCH_TITLE: str = Field("", description="french item title")
    ENGLISH_TITLE: str = Field("", description="english title of the item")
    FRENCH_DESCRIPTION: str = Field("", description="Description of the item itself")
    ENGLISH_DESCRIPTION: str = Field("", description="Description of the item itself")
    NUMBER_OBJECTS_DESCRIBED: str = Field(
        "", description="Total number of object found in description"
    )
    CLEAN_OBJECT_CATEGORY: str = Field(
        "", description="cleaned category found from object category LLM"
    )
    STATUS: str = Field(
        "", description="KO if the CLEAN_OBJECT_CATEGORY is null, OK otherwise"
    )
