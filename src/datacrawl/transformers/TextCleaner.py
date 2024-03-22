from typing import List
import pandas as pd 

import re
import numpy as np
from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from src.constants.variables import currencies
from omegaconf import DictConfig


class TextCleaner(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)

    def get_list_element_from_text(self, variable, liste=currencies):
        return variable.apply(lambda x : re.findall(liste, str(x))[0] if 
                                             len(re.findall(liste, str(x))) > 0 else np.nan)

    def get_estimate(self, variable, min_max : str = "min"):
        if min_max.lower() == "min":
            return variable.apply(lambda x : re.findall(r"\d+", str(x).replace(" ","").replace(",",""))[0] 
                                           if len(re.findall(r"\d+", str(x).replace(" ","").replace(",",""))) > 0 else np.nan)
        elif min_max.lower() == "max":
            return variable.apply(lambda x : re.findall(r"\d+", str(x).replace(" ","").replace(",",""))[1] 
                                           if len(re.findall(r"\d+", str(x).replace(" ","").replace(",",""))) > 1 else np.nan)
        else: 
            raise Exception("EITHER MIN OR MAX value for min_max")

    def get_splitted_infos(self, variable, index, sep='\n'):
        return  pd.DataFrame(variable.str.split(sep).tolist(), index=index)
    
    def remove_missing_values(self, df):

        important_cols =["FINAL_RESULT", "CURRENCY", "URL_FULL_DETAILS", "INFOS"]

        if self.check_cols_exists(important_cols, df.columns):
            shape_0 = df.shape[0]
            df = df.loc[(df["FINAL_RESULT"].notnull())&(
                        df["CURRENCY"].notnull())&(
                        df["URL_FULL_DETAILS"].notnull())&(
                        df["INFOS"].notnull())].reset_index(drop=True) 
            shape_1 = df.shape[0]
            self._log.info(f"REMOVING {shape_0 - shape_1} \
                        ({(shape_0-shape_1)*100/shape_0:.2f}%) OBS due to lack of curcial infos")
            return df 
        else:
            missing_cols = set(important_cols) - set(df.columns)
            raise Exception(f"FOLLOWING COLUMN(S) IS MISSING {missing_cols}")
        
    
    def clean_estimations(self, df : pd.DataFrame, liste_exceptions : List):

        important_cols = ["FINAL_RESULT", "MIN_ESTIMATION", "MAX_ESTIMATION"]

        if self.check_cols_exists(important_cols, df.columns):
            for col in important_cols:
                df[col] = np.where(df[col].isin(liste_exceptions), 
                                    np.nan, df[col])
                df[col] = df[col].astype(float)
            
            df["FINAL_RESULT_EXISTS"] = 1*(df["FINAL_RESULT"].notnull())
            df["FINAL_RESULT"] = np.where(df["FINAL_RESULT"].isnull(), 
                                        df[["MIN_ESTIMATION", "MAX_ESTIMATION"]].mean(axis=1), 
                                        df["FINAL_RESULT"])
            return df
        else:
            missing_cols = set(important_cols) - set(df.columns)
            raise Exception(f"FOLLOWING COLUMN(S) IS MISSING {missing_cols}")
        
    
    def check_cols_exists(self, cols_a, cols_b):
        return len(set(cols_a).intersection(set(cols_b))) == len(cols_a)
    