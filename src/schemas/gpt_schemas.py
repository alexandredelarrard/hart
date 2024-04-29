from pydantic import BaseModel, Field

class Painting(BaseModel):
    artirst_surname : str = Field(description="question to set up a joke")
    artirst_name: str = Field(description="question to set up a joke")
    painting_title: str = Field(description="question to set up a joke")
    is_painted_by_artist: bool = Field(description="question to set up a joke")
    signature_location: str = Field(description="question to set up a joke")
    is_dated: bool = Field(description="question to set up a joke")
    painting_length: str = Field(description="question to set up a joke")
    painting_width: str = Field(description="question to set up a joke")
    painting_support_material: str = Field(description="question to set up a joke")
    painting_condition: str = Field(description="question to set up a joke")
    painting_material: str = Field(description="question to set up a joke")
    painting_periode_or_year: str = Field(description="question to set up a joke")

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
                    "watch": Watch}
    
    if object not in mapping_object.keys():
        raise Exception(f"{object} not handled yet by pydentic schemas, please add to the schema or change object")
    else:
        return mapping_object[object]