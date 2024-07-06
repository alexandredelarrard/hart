import re
from typing import List, Dict
import logging
from src.utils.utils_dataframe import remove_accents
import warnings

warnings.simplefilter("ignore")


def reconstruct_dict(x):
    new_dict = []
    a = x.split("\n")
    count_element = 0
    for element in a:
        if element == "":
            pass
        else:
            if element == "{":
                count_element += 1
            if ": " in element:
                key, value = element.split(": ", 1)
                key = key.replace('"', "").strip()
                value = (
                    value.replace('"', "")
                    .replace("\\", "")
                    .replace(",", "")
                    .split("//")[0]
                    .strip()
                )
                element = f'"{key}": "{value}",'
            new_dict.append(element)

    if new_dict[-1] != "}":
        new_dict.append("}")

    answer = "\n".join(new_dict)
    answer = answer.replace('"[",', "[")
    answer = answer.replace('"{",', "{")

    if "}\n{" in answer:
        answer = "[" + answer + "]"
        answer = answer.replace("}\n{", "},\n{")

    return eval(answer)


def handle_answer(answer):

    x = answer["ANSWER"]
    if isinstance(x, dict):
        return x

    if x[:5] == "Here ":
        x = x.split(":", 1)[-1]

    x = x.replace("false", '"False"')
    x = x.replace("true", '"True"')
    x = x.replace("null", '"Null"')
    x = x.replace("N/A", '"None"')
    x = x.replace("```json", "")
    x = x.replace("```", "")
    x = x.replace('""', '"')
    x = x.strip()

    # handle lists
    if len(re.findall("\\[(.*?)\\]", x)) != 0:
        origin, new_element = clean_list(x)
        x = x.replace(origin, new_element)

    try:
        x = eval(x)
        return x

    except Exception:
        try:
            return reconstruct_dict(x)
        except Exception:
            logging.error(answer["ID_ITEM"])
            return "{}"


def clean_list(x):
    origin = re.findall("\\[(.*?)\\]", x)[0]
    liste = origin.split(",")
    new_element = ""
    for element in liste:
        clean_element = (
            element.replace('"', "").replace("'", "").replace("\\", "").strip()
        )
        new_element += f'"{clean_element}", '
    return origin, new_element


def homogenize_value_format(value):
    if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
        return remove_accents(str(value).lower())
    elif isinstance(value, List):
        liste = []
        for element in value:
            liste.append(homogenize_value_format(element))
        return liste
    elif isinstance(value, Dict):
        new_dict = {}
        for key, val in value.items():
            new_dict[key] = homogenize_value_format(val)
        return new_dict
    else:
        return value


def replace_key(k, col_mapping):
    for feature, liste_features in col_mapping.items():
        k = homogenize_value_format(k).replace(" ", "_")
        if k in liste_features:
            return feature
    return k


def homogenize_keys_name(x, col_mapping, smooth_text=True):
    new_dict = {}
    try:
        for k, v in x.items():
            key = replace_key(k, col_mapping)
            if isinstance(v, List):
                values = []
                for sub_values in v:
                    if smooth_text:
                        values.append(remove_accents(str(sub_values).lower().strip()))
                    else:
                        values.append(remove_accents(str(sub_values).strip()))
                new_dict[key] = values
            else:
                if smooth_text:
                    new_dict[key] = remove_accents(str(v).lower().strip())
                else:
                    new_dict[key] = remove_accents(str(v).strip())
        return new_dict
    except Exception:
        logging.warning(x)
        return x
