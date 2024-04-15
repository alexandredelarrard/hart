import re 
import unidecode
import numpy as np
import string
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


def transform_types(dtype : Dict) -> Dict:
    for i, v in dtype.items():
        try:
            dtype[i] = eval(v)# float if v=="float" else ( int if v=="int" else str)
        except ValueError as e:
            print(e)
            pass
    return dtype

def remove_accents(x):
    return unidecode.unidecode(x)

def remove_punctuation(x):
    return re.sub("[^A-Za-z0-9_]+", " ", x)  # only alphanumeric characters and underscore are allowed


def flatten_dict(mapping_dict):
    flat_dict = {}
    for key, values in mapping_dict.items():
        for value in values:
            flat_dict[value] = key
    return flat_dict


def map_value_to_key(x, mapping_dict):

    for key, values in mapping_dict.items():
        for sub_value in values:
            if str(sub_value)==str(x).strip():
                return key
            
    return x