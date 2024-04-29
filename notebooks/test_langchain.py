from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from typing import List, Optional

class Painting(BaseModel):
    is_a_painting: bool = Field(description="Do we describe a painting or something else ? An icone is not a painting, a drawing either, etc.")
    object_described: Optional[str] = Field(description="If the object described is not a painting, write what kind of object is described")
    artirst_surname : str = Field(description="Surname of the artist")
    artirst_name: str = Field(description="Name of the artist")
    painting_title: str = Field(description="Title of the painting")
    is_painted_by_artist: bool = Field(description="Is this painting painted by the artist or the school / copy of the artist style ?")
    signature_location: str = Field(description="Where is the signature of the artist on the painting if there is one ?")
    is_dated: bool = Field(description="Is the painting dated")
    painting_length: str = Field(description="Length of the painting in cm. Convert to centimeters if necessary")
    painting_width: str = Field(description="Width of the painting in cm. Convert to centimeters if necessary")
    painting_support_material: str = Field(description="What material the painting has been painted on ? For instance canvas, wood, paper, etc.")
    is_framed: bool = Field(description="Is the painting framed ?")
    painting_condition: Optional[str] = Field(description="Is the painting in good condition ? Is there scratches, holes, etc ?")
    painting_material: str = Field(description="What material has been used to do the painting? Example: oil, gouache, watercolor, etc.")
    painting_periode_or_year: str = Field(description="Year the painting was painted or circa year or period")

client = ChatOpenAI(model="gpt-3.5-turbo-0125",
                    openai_api_key="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", 
                    temperature=0)

introduction="You are an art expert. Extract following features from the painting description with a JSON format. Only return valid json and nothing else. Write all JSON values only in english, translate them if necessary. If no information is provided, render na." 

# Set up a parser + inject instructions into the prompt template.
parser = JsonOutputParser(pydantic_object=Painting)

prompt = PromptTemplate(
    template=introduction + "\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = prompt | client | parser

description="""Alexandre ROUBTZOFF (Saint-Pétersbourg, 1884 - Tunis, 1949)
Vue de Meded (1940)
Huile sur toile marouflée sur carton, signée et datée en bas à droite « A. Roubtzoff. 1940. 18 sept. » et localisé en bas à gauche « Meded ». Encadré.
H. 19,8 x L. 28 cm.
Provenance
- Cadeau de l’artiste au docteur Éloi Baysse, médecin de colonisation en Tunisie (nommé en 1934), également ami et médecin de l’artiste.
- Puis par descendance."""
chain.invoke({"query": description})

description="""Icône russe du XIXe siècle encadrée avec rizza : "Madone et enfant" - 17 x 13,5"""
chain.invoke({"query": description})