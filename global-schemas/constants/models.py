from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, List, Any


class BaseResult(BaseModel):
    distance: float | int = Field(
        ..., description="Distance to the provided embedding and database"
    )
    id_picture: str | float | None = Field(
        None, description="Picture ID based on item pictures in database"
    )


class EmbeddingsResults(BaseModel):
    answer: Dict[str, BaseResult] = Field(default_factory=dict)


class MultiEmbeddingsResults(BaseModel):
    image: EmbeddingsResults = Field(default_factory=dict)
    text: EmbeddingsResults = Field(default_factory=dict)


class FullResultInfos(BaseModel):
    id_item: str = Field(..., description="Item ID")
    id_picture: str = Field(..., description="Picture ID")
    pictures: list[str] = Field(..., description="String with comma-separated elements")
    title: str | None = Field(..., description="Title of the item")
    description: str = Field(..., description="Description of the item")
    estimate_min: float | None = Field(..., description="Minimum estimate")
    estimate_max: float | None = Field(..., description="Maximum estimate")
    localisation: str | None = Field(..., description="Location of the item")
    final_result: float | None = Field(..., description="Final result of the item")
    date: str = Field(..., description="Date of the result")
    seller: str = Field(..., description="Seller of the item")
    house: str = Field(..., description="House of the item")
    url_full_detail: str = Field(..., description="URL for full detail")
    distance: float = Field(
        None, description="Distance to the provided embedding and database"
    )


class KnnFullResultInfos(BaseModel):
    answer: List[FullResultInfos]
