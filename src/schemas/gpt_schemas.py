from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional

class Painting(BaseModel):
    artirst_surname : str = Field(description="Surname of the artist")
    artirst_name: str = Field(description="Name of the artist")
    painting_title: str = Field(description="Title of the painting")
    is_painted_by_artist: bool = Field(description="Is this painting painted by the artist ? If painted by the school / copy of the artist style then answer False")
    is_signed: bool = Field(description="Is the painting signed by the artist ?")
    is_dated: bool = Field(description="Is the painting dated ?")
    is_framed: bool = Field(description="Is the painting framed ?")
    painting_length: str = Field(description="Length of the painting in cm. Convert to centimeters if necessary. For instance if written 24 x 36 inch (61 x 91.4 cm.) you should write 61 cm")
    painting_width: str = Field(description="Width of the painting in cm. Convert to centimeters if necessary. For instance if written 24 x 36 inch (61 x 91.4 cm.) you should write 91.4 cm")
    painting_support_material: str = Field(description="What material the painting has been painted on ? For instance canvas, wood, paper, etc.")
    painting_material: str = Field(description="What material has been used to do the painting? Example: oil, gouache, watercolor, etc.")
    painting_condition: Optional[str] = Field(description="Is the painting in good condition ? Is there scratches, holes, etc ?")
    painting_period_or_year: str = Field(description="Year the painting was painted or circa year or period")
    number_objects_described: str = Field(description="The number of objects described in the text")

class Sculpture(BaseModel):
    is_a_sculpture: bool = Field(description="Do we describe a sculpture or something else ? False if this is a mask, a vase, etc.")
    object_described: Optional[str] = Field(description="If the object described is not a sculpture, write what kind of object is described")
    artirst_surname : str = Field(description="Surname of the artist. Render the school of the sculpture if available")
    artirst_name: str = Field(description="Name of the artist")
    sculpture_subject: str = Field(description="What is the sculpture representing ?")
    sculpture_height: str = Field(description="Height of the sculpture in cm. Convert to centimeters if necessary")
    sculpture_width: str = Field(description="Width of the sculpture in cm. Convert to centimeters if necessary")
    sculpture_length: str = Field(description="Length of the sculpture in cm. Convert to centimeters if necessary")
    signature_location: str = Field(description="Where is the signature of the artist on the sculpture if there is one ?")
    sculpture_condition: Optional[str] = Field(description="Is the sculpture in good condition ? Is there scratches, holes, etc ?")
    sculpture_color: str = Field(description="What color is the sculpture ? Render the material color if available")
    sculpture_material: str = Field(description="What material has been used to do the sculpture? Example: marble, wood, earthstone, etc.")
    sculpture_periode_or_year: str = Field(description="Year the sculpture was done or century/period")
    number_objects_described: str = Field(description="The number of objects described in the text")

class Vase(BaseModel):
    object_category : str
    number_described_objects: int
    is_a_vase: bool
    vase_shape: str
    vase_style: str
    vase_material: str 
    vase_color: str 
    vase_periode_or_circa_year: str
    vase_height: str
    vase_decoractions: str
    vase_signed: str
    vase_condition: str
    vase_origin_country: str

class Watch(BaseModel):
    watch_brand: str
    watch_category: str 
    watch_model_or_collection_name: str 
    watch_movement: str 
    gender : str 
    watch_circa_year_or_period: str 
    dial_material: str 
    dial_color: str 
    dial_luminous:bool 
    case_or_dial_shape: str 
    case_material: str 
    case_size: str 
    watch_reference: str 
    bracelet_or_strap_material: str 
    number_jewels: int 
    jewels_type: str 
    bracelet_or_strap_color: str 
    dial_or_case_diameter: str  
    watch_weight: str 
    watch_serial_number: str 
    buckle_or_clasp: str 
    buckle_or_clasp_type: str 
    dial_signature: str 
    case_signature: str 
    hour_marker_style: str 
    minute_index_style: str 
    hands_material: str 
    hands_style: str 
    is_date_displayed: bool
    crystal_condition: str 
    watch_functionning: bool 
    limited_edition: str 
    water_resistant: bool 
    has_certificate: bool 
    is_certified: bool
    has_chronometer_chronograph: bool 
    number_subdial: int 
    has_package_box: bool 
    under_warranty: bool 
    type_of_jewels: str 
    number_carats: str 
    case_back: str 
    bracelet_length: str 
    watch_condition: str 
    crown_material: str 
    glass_material: str 
    has_moon_phase: str

def get_mapping_pydentic_object(object : str):
    mapping_object= {"painting": Painting,
                    "vase": Vase,
                    "watch": Watch,
                    "sculpture": Sculpture}
    
    if object not in mapping_object.keys():
        raise Exception(f"{object} not handled yet by pydentic schemas, please add to the schema or change object")
    else:
        return mapping_object[object]