import re
import numpy as np
from typing import List, Dict
import logging 
from src.utils.utils_dataframe import remove_accents, remove_punctuation

def reconstruct_dict(x):
    new_dict= []
    a = x.split("\n")
    for element in a: 
        if ": " in element:
            key, value = element.split(": ")
            key = key.replace("\"", "").strip()
            value = value.replace("\"", "").replace(",","").strip()
            element = f"\"{key}\": \"{value}\","
        new_dict.append(element)
    return eval("\n".join(new_dict))


def handle_answer(x):

    x = x.replace("false", "False")
    x = x.replace("true", "True")
    x = x.replace("null", "\"Null\"")
    x = x.replace("```json", "")
    x = x.replace("```", "")
    x = x.replace("N/A", "None")
    
    # handle lists 
    if len(re.findall("\\[(.*?)\\]", x)) !=0: 
        origin, new_element = clean_list(x)
        x = x.replace(origin, new_element)

    try: 
        x = eval(x)
        return x
    
    except Exception:
        try:
            return reconstruct_dict(x)
        except Exception:
            logging.error(x)
            return "{}"
            
    
def clean_list(x):
    origin = re.findall("\\[(.*?)\\]", x)[0]
    liste = origin.split(",")
    new_element = ""
    for element in liste:
        clean_element = element.replace("\"", "").replace("\'", "").replace("\\", "").strip()
        new_element+= f"\"{clean_element}\", "
    return origin, new_element


def homogenize_value_format(value):
    if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
        return remove_accents(value.lower())
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

def homogenize_keys_name(x, col_mapping):
    new_dict = {}
    for k, v in x.items():
        key =  replace_key(k, col_mapping)
        new_dict[key] = remove_accents(str(v).lower().strip())
    return new_dict


### OLD
def flatten_dict(subdict, key):
    new_sub_dict = {}
    for sub_key, sub_value in subdict.items():
        new_sub_dict["_".join([key, sub_key])]= sub_value
    return new_sub_dict


def flatten_description(x):

    final_dict = {}

    try:
        for key, value in x.items():
            if isinstance(value, List):
                if len(value) !=0:
                    if isinstance(value[0], str):
                        final_dict[key] = ", ".join(value)

                    elif isinstance(value[0], Dict):
                        for subdict in value:
                            new_sub_dict = flatten_dict(subdict, key)
                            final_dict = {**final_dict, **new_sub_dict}
                    
            elif isinstance(value, Dict):
                new_sub_dict = flatten_dict(value, key)
                final_dict = {**final_dict, **new_sub_dict}

            else:
                final_dict[key] = value
        
        return final_dict
    
    except Exception:
        logging.error(x)
        