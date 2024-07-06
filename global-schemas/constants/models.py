from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator
)

class EmbeddingsResults(BaseModel):
    ids: list[str] = Field(default_factory=list)
    distances: list[float] = Field(default_factory=list)