import re 
import unidecode
import numpy as np
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
        new_var = unidecode.unidecode(new_var)
        new_var = re.sub("[^A-Za-z0-9_]+", "_", new_var)  # only alphanumeric characters and underscore are allowed
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