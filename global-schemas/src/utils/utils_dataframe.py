import re
import unidecode
import numpy as np
import ast
from typing import List, Dict


def homogenize_columns(col_names: List) -> List:
    """Rename columns to upper case and remove space and
    non conventional elements

    Args:
        col_names (List): original column names

    Returns:
        List: clean column names
    """

    new_list = []
    for var in col_names:
        var = str(var).replace("/", " ")  # replace space by underscore
        new_var = re.sub("[ ]+", "_", str(var))  # replace space by underscore
        new_var = remove_accents(new_var)
        new_var = re.sub("[^A-Za-z0-9_]+", "_", new_var)
        new_var = re.sub("_$", "", new_var)  # variable name cannot end with underscore
        new_var = new_var.upper()  # all variables should be upper case
        new_list.append(new_var)
    return new_list


def transform_types(dtype: Dict) -> Dict:
    for i, v in dtype.items():
        try:
            dtype[i] = ast.literal_eval(
                v
            )  # float if v=="float" else ( int if v=="int" else str)
        except ValueError as e:
            print(e)
            pass
    return dtype


def remove_accents(x):
    return unidecode.unidecode(x)


def remove_punctuation(x):
    return re.sub(
        "[^A-Za-z0-9_]+", " ", x
    )  # only alphanumeric characters and underscore are allowed


def flatten_dict(mapping_dict):
    flat_dict = {}
    for key, values in mapping_dict.items():
        for value in values:
            flat_dict[value] = key
    return flat_dict


def map_value_to_key(x, mapping_dict):

    for key, values in mapping_dict.items():
        for sub_value in values:
            if str(sub_value) == str(x).strip():
                return key

    return x


# utils functions
def clean_useless_text(x):
    x = str(x)
    x = x.replace("Lot Details\n", "")
    x = x.replace("Description\n", "")
    x = x.replace("Authenticity guaranteed", "")
    x = x.replace("Photo non contractuelle", "")
    x = x.replace("No reserve\n", "")
    x = x.replace("DETAILS\n", "")
    return x


def remove_dates_in_parenthesis(x):
    pattern = re.compile(r"\([0-9-]+\)")
    return re.sub(pattern, "", x)


def clean_dimensions(x):
    pattern1 = re.compile(r"(\d+.?\d+[ xX]+\d+.?\d+[ xX]+\d+.?\d+)")
    origin = re.findall(pattern1, x)
    if len(origin) == 1:
        origin = origin[0]
        numbers = origin.lower().split("x")
        if len(numbers) == 3:
            new = f" hauteur: {numbers[0].strip()}; largeur: {numbers[1].strip()}; profondeur: {numbers[2].strip()}"
            return x.replace(origin, new)

    pattern2 = re.compile(r"(\d+.?\d+[ xX]+\d+.?\d+)")
    origin = re.findall(pattern2, x)
    if len(origin) == 1:
        origin = origin[0]
        numbers = origin.lower().split("x")
        if len(numbers) == 2:
            new = f" longueur: {numbers[0].strip()}; largeur: {numbers[1].strip()}"
            return x.replace(origin, new)
    return x


def clean_quantity(x):
    x = re.sub(r"(H[\s.:])[\s.:\d+]", " hauteur ", x, flags=re.I)
    x = re.sub(r"(L[\s.:])[\s.:\d+]", " longueur ", x, flags=re.I)
    x = re.sub(r"(Q[\s.:])[\s.:\d+]", " quantite ", x, flags=re.I)
    return x


def clean_shorten_words(x):
    x = re.sub(r"[\s\d+\s](B)\s", " bouteille ", x, flags=re.I, count=1)
    x = re.sub(" bout. ", " bouteille ", x, flags=re.I, count=1)
    x = re.sub(" bt. ", " bouteille ", x, flags=re.I, count=1)
    x = re.sub("(bt)", " bouteille ", x, flags=re.I, count=1)
    x = re.sub("(mag)", " magnum ", x, flags=re.I, count=1)
    x = re.sub("@", "a", x)
    x = re.sub("n°", " numéro ", x)
    x = re.sub(" in. ", " inch ", x, flags=re.I)
    x = re.sub(" ft. ", " feet ", x, flags=re.I)
    x = re.sub(" approx. ", " approximativement ", x)
    x = re.sub(" g. ", " gramme ", x, flags=re.I)
    x = re.sub(" gr. ", " gramme ", x, flags=re.I)
    x = re.sub(" diam. ", " diametre ", x, flags=re.I)
    x = x.replace("¾", "3/4")
    x = x.replace("¼", "3/4")
    x = x.replace("⅐", "1/7")
    x = x.replace("½", "1/2")
    return x


def remove_spaces(x):
    x = str(x).strip()
    x = re.sub(" +", " ", x)
    return x


def remove_lot_number(x):
    return re.sub(r"^(\d+\. )", "", str(x))


def remove_rdv(x):
    x = str(x).split("\nEstimate")[0]
    x = str(x).split("\nSans rendez-vous")[0]
    x = str(x).split("\nCondition Report\nProvenance")[0]
    x = str(x).split("\nProvenance")[0]
    x = str(x).split("Les rapports de condition sont")[0]
    x = str(x).split("Le meuble ne peut être vu")[0]
    x = str(x).split("A lire attentivement :")[0]
    x = str(x).split("voir la suite de la description sur le certificat")[0]
    x = str(x).split("Pour enchérir, veuillez consulter la section")[0]
    x = str(x).split("Catalogue Note\n")[0]
    x = str(x).split("\nAdditional Notices")[0]
    x = str(x).split("\nPROVENANCE")[0]
    x = str(x).split("In response to your inquiry, we are")[0]
    x = str(x).split("NOTWITHSTANDING THIS REPORT OR ANY")[0]
    x = str(x).split("Dans le cadre de nos activités de ventes aux enchères")[0]
    x = str(x).split("Délivrance : sur")[0]
    x = str(x).split("Expédition : se")[0]
    x = str(x).split("**Please be advised that")[0]
    x = str(x).split("\nUne TVA de")[0]
    return x
