from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from src.constants.variables import DATE_HOUR_FORMAT


class LlmExtraction(BaseModel):
    __tablename__ = "_raw_gpt_extraction"
    __table_args__ = {"extend_existing": True}

    id_item: str = Field(None, description="unique id of the extraction to do")
    methode: str = Field(None, description="LLM methode used to extract json")
    input: str = Field("", description="Input sent to the LLM")
    prompt_schema: str = Field(None, description="Schema to follow as an output")
    answer: BaseModel | dict = Field({}, description="LLM output")
    date_run: str = Field(
        datetime.now().strftime(DATE_HOUR_FORMAT), description="Date when the LLM ran"
    )


class BaseFeature(BaseModel):
    object_category: str = Field(
        description="The specific category of the described object. Be very specific, write the answer in English only. Examples include: painting, table, serigraphy, vase, lamp, ring, etc. Never give generic categories such as 'accessories', 'jewelry', 'furniture', 'decorative object'"
    )
    number_objects_described: str = Field(
        description="The number of objects described in the text. If only one object is described, enter '1'. If it is a pair, enter '2', etc."
    )


class Reformulate(BaseFeature):
    french_title: str = Field(
        description="Few words in French, presenting what the art description is about."
    )
    french_description: str = Field(
        description="The detailed art description translated into French."
    )
    english_title: str = Field(
        description="Few words in English, presenting what the art description is about."
    )
    english_description: str = Field(
        description="The detailed art description in English."
    )


class Painting(BaseFeature):
    artirst_surname: str = Field(description="Surname of the artist")
    artirst_name: str = Field(description="Name of the artist")
    painting_title: str = Field(description="Title of the painting")
    is_painted_by_artist: str = Field(
        description="Is this painting painted by the artist ? Answer by True, False or None if not written. If painted by the school or copy of the artist then answer False. "
    )
    is_signed: str = Field(
        description="Is the painting signed by the artist ? Answer by True, False or None if not written"
    )
    is_dated: str = Field(
        description="Is the painting dated ? Answer by True, False or None if not written"
    )
    is_framed: str = Field(
        description="Is the painting framed ? Answer by True, False or None if not written"
    )
    painting_length: str = Field(
        description="Length of the painting in cm. Convert to cm if necessary and always give the unit."
    )
    painting_width: str = Field(
        description="Width of the painting in cm. Convert to cm if necessary and always give the unit."
    )
    painting_support_material: str = Field(
        description="What material the painting has been painted on ? For instance canvas, wood, paper, etc."
    )
    painting_material: str = Field(
        description="What material has been used to do the painting? Example: oil, gouache, watercolor, etc."
    )
    painting_condition: str = Field(
        description="Is the painting in good condition ? Is there scratches, holes, etc ?"
    )
    painting_period_or_year: str = Field(
        description="Year, circa year or century when the painting was painted."
    )


class Ring(BaseFeature):
    ring_typology: str = Field(
        description="Ring typologie. For instance, a solitary, a perl ring, an alliance, engagement, three stones settings, marguerite, etc."
    )
    ring_brand: str = Field(
        description="Ring brand, ring maker or engraved mark / hallmark. For instance, Cartier, Lecoutre, etc."
    )
    ring_material: str = Field(
        description="Material of the ring. For instance, yellow gold, white gold, platinium and silver, etc. Only render material inforamtion. "
    )
    ring_material_purety: str = Field(
        description="Purety of the metal which makes the ring. For instance 14k, 18k, 800/1000, 750 °/°°, etc."
    )
    central_ring_stone_kind: str = Field(
        description="If there is a central stone, what kind of stone is it ? For instance: Ruby, Diamond, Saphir, Opal, Emerald, Perle, etc."
    )
    central_ring_stone_weight: str = Field(
        description="Total weight of central ring. Can be in grammes of in carats (written sometimes ct or cts)"
    )
    central_ring_stone_number: str = Field(
        description="Number of stones the central part has. For instance for 2 x 0.5 carats, answer 2"
    )
    central_ring_stone_color: str = Field(
        description="If central stone is a diamond, the color of the diamond. Can take values as capital letters between D and Z. Usually J, K, L, M."
    )
    central_ring_stone_shape: str = Field(
        description="Shape of central stone. For example caboshon, pear sahpe, round shape, etc."
    )
    central_ring_stone_purity: str = Field(
        description="Purity or the central ring stone. Usually FL, IF, VVS 1 or 2, VS 1 or 2, SI 1 or 2, etc. "
    )
    central_ring_stone_cut: str = Field(
        description="Central stone cut quality. Can go from very poor to excellent."
    )
    central_ring_stone_size: str = Field(
        description="Diameter of the central stone. Can be in mm if this is a pearl."
    )
    side_ring_number: str = Field(
        description="Stone number the ring has around the central stone, if any. Only give a number if there is a central stone"
    )
    side_ring_kind: str = Field(
        description="Kind of stone the ring has around its center if any (diamond, perls, rubys, stone, etc.)."
    )
    side_ring_weight: str = Field(
        description="Weight of side rings. Can be in grammes of in carats (written ct, cts or carats)"
    )
    total_ring_weight: str = Field(
        description="Total weight of the ring. Usually written in grammes. Render only the ring weight and not the stone weight."
    )
    ring_period_or_year: str = Field(
        description="Year, circa year, periode or century when the ring was created."
    )
    ring_size: str = Field(
        description="What finger size is the ring ? Can be identified by TDD (tour de doigt) or size. Values between 40 to 60"
    )
    ring_condition: str = Field(
        description="Condition of the ring. Any missing part, scratch or lack of luminosity should appear here. Summarize condition in maximum 5 words"
    )


class Sculpture(BaseFeature):
    object_category: str = Field(
        description="What kind of object this description is talking about? Be very specific in the object category. for instance: Painting, table, chair, serigraphie, etc."
    )
    object_described: Optional[str] = Field(
        description="If the object described is not a sculpture, write what kind of object is described"
    )
    artirst_surname: str = Field(
        description="Surname of the artist. Render the school of the sculpture if available"
    )
    artirst_name: str = Field(description="Name of the artist")
    sculpture_subject: str = Field(description="What is the sculpture representing ?")
    sculpture_height: str = Field(
        description="Height of the sculpture in cm. Convert to centimeters if necessary"
    )
    sculpture_width: str = Field(
        description="Width of the sculpture in cm. Convert to centimeters if necessary"
    )
    sculpture_length: str = Field(
        description="Length of the sculpture in cm. Convert to centimeters if necessary"
    )
    signature_location: str = Field(
        description="Where is the signature of the artist on the sculpture if there is one ?"
    )
    sculpture_condition: Optional[str] = Field(
        description="Is the sculpture in good condition ? Is there scratches, holes, etc ?"
    )
    sculpture_color: str = Field(
        description="What color is the sculpture ? Render the material color if available"
    )
    sculpture_material: str = Field(
        description="What material has been used to do the sculpture? Example: marble, wood, earthstone, etc."
    )
    sculpture_periode_or_year: str = Field(
        description="Year the sculpture was done or century/period"
    )
    number_objects_described: str = Field(
        description="The number of objects described in the text"
    )


class Vase(BaseFeature):
    object_category: str
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


class Watch(BaseFeature):
    watch_brand: str
    watch_category: str
    watch_model_or_collection_name: str
    watch_movement: str
    gender: str
    watch_circa_year_or_period: str
    dial_material: str
    dial_color: str
    dial_luminous: bool
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


def get_mapping_pydentic_object(object: str):
    mapping_object = {
        "painting": Painting,
        "vase": Vase,
        "watch": Watch,
        "ring": Ring,
        "sculpture": Sculpture,
        "reformulate": Reformulate,
    }

    if object not in mapping_object.keys():
        raise Exception(
            f"{object} not handled yet by pydentic schemas, please add to the schema or change object"
        )
    else:
        return mapping_object[object]
