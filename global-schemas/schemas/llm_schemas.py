from langchain_core.pydantic_v1 import BaseModel, Field


class Designation(BaseModel):
    french_title: str = Field(
        description="The title of the art description translated into French."
    )
    french_description: str = Field(
        description="The detailed art description translated into French."
    )
    english_title: str = Field(
        description="The title of the art description in English."
    )
    english_description: str = Field(
        description="The detailed art description in English."
    )
    object_category: str = Field(
        description="The specific category of the described object. Be very specific and provide the answer in English only. Examples include: painting, table, serigraphy, vase, lamp, ring, or another specific item."
    )
    number_objects_described: str = Field(
        description="The number of objects described in the text. If only one object is described, enter '1'. If it is a pair, enter '2', etc."
    )


def get_mapping_pydentic_object(object: str):
    mapping_object = {"designation": Designation}

    if object not in mapping_object.keys():
        raise Exception(
            f"{object} not handled yet by pydentic schemas, please add to the schema or change object"
        )
    else:
        return mapping_object[object]
