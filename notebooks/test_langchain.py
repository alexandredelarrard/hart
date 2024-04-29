from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from typing import List, Optional

class Painting(BaseModel):
    is_a_painting: bool = Field(description="Do we describe a painting or something else ? False if this is an icone a drawing, a print, etc.")
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


class Sculpture(BaseModel):
    sculpture_category: bool = Field(description="What kind of sculpture is this object about ? It can be a bust, a sculpture, a figurine, etc.")
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

client = ChatOpenAI(model="gpt-3.5-turbo-0125",
                    openai_api_key="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", 
                    temperature=0)

introduction="You are an art expert. Extract following features from the painting description with a JSON format. Only return valid json and nothing else. Write all JSON values only in english, translate them if necessary. If no information is provided, render na." 

# Set up a parser + inject instructions into the prompt template.
parser = JsonOutputParser(pydantic_object=Sculpture)

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

description="""École ITALIENNE du XVIe siècle
Jeune enfant au drapé
Buste en marbre blanc.
Porte une étiquette au revers du piédouche 3285.
Porte une étiquette sur le socle n° 3285 / Acht 1951 / Buste Romain / P.A. 2000.
H. 32 cm dont piédouche H. 11,5 cm
Accidents au nez et dans le drapé."""
chain.invoke({"query": description})

description="""François Pompon (1855 Saulieu - 1933 Paris) d'après
Ours polaire
Bronze, patine foncée. Fonte posthume contemporaine, début du 21e siècle ; représentation d'un ours marchant vers la droite. Sculpture en bronze stylisée de manière moderne d'après la célèbre sculpture en marbre de Pompon "Ours blanc", considérée comme son œuvre la plus aboutie et qui lui permit de percer au Salon de Paris en 1922 - des exemplaires de cette sculpture se trouvent au Museum of Modern Art de New York et au Musée d'Orsay à Paris. Pompon a travaillé dans l'atelier d'Auguste Rodin et de Camille Claudel. Après 1905, il s'est consacré exclusivement à la représentation animale. H. 45 cm ; L. env. 85 cm.
Après François Pompon (1855 - 1933). Bronze patiné foncé. Posthume, fonte contemporaine, début du XXIe siècle."""
chain.invoke({"query": description})

description="""FRANCIS RENAUD (1887-1973)
BUSTE D'HOMME
Terre cuite
Signée à droite sur la terrasse
Terracotta; signed on the right of the terrace

HAUTEUR : 42 CM • HEIGHT : 16 1/2 IN."""
