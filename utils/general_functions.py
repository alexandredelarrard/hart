import time
import re
import numpy as np
import pandas as pd
from typing import List
import unidecode
import scipy as sp

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f s' % \
                  (method.__name__, (te - ts)))
        return result

    return timed

def smart_column_parser(col_names: List) -> List:
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
        new_var = re.sub(
            "[^A-Za-z0-9_]+", "", new_var
        )  # only alphanumeric characters and underscore are allowed
        new_var = re.sub("_$", "", new_var)  # variable name cannot end with underscore
        new_var = new_var.upper()  # all variables should be upper case
        new_list.append(new_var)
    return new_list


def concatenate_keys(datas):

    full_loc = pd.DataFrame()
    for key in datas.keys():
        sub = datas[key]
        sub["DATE_EXTRACT"] = key 
        full_loc = pd.concat([full_loc, sub], axis=0)

    return full_loc


def homogenize_modalities(x):

    x = unidecode.unidecode(x)
    x = re.sub("[-:;'/,.?!]"," ", x)
    x = x.upper()
    x =  re.sub(" EME", "", x).strip()
    x =  re.sub(" ER", "", x).strip()
    x =  re.sub("ARRONDISSEMENT", " ", x).strip()

    return x


def exp_func(x, a, b, c):
    return a * np.exp(-b * x) + c


def polynome(x, value):
    return x[3] + x[2]*value + x[1]*value**2 + x[0]*value**3


def fit_curve(x, y, p0, function=exp_func):
    try:
        params, cv = sp.optimize.curve_fit(function, x, y, p0, maxfev = 1000)
    except Exception:
        params = [0, 0, np.median(y)]
    return params
