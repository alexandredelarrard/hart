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

        important_cols =[self.name.item_result, 
                        self.name.currency, 
                        self.name.url_full_detail, 
                        self.name.item_infos]

        if self.check_cols_exists(important_cols, df.columns):
            shape_0 = df.shape[0]
            df = df.loc[(df[self.name.item_result].notnull())&(
                        df[self.name.currency].notnull())&(
                        df[self.name.url_full_detail].notnull())&(
                        df[self.name.item_infos].notnull())].reset_index(drop=True) 
            shape_1 = df.shape[0]
            self._log.info(f"REMOVING {shape_0 - shape_1} \
                        ({(shape_0-shape_1)*100/shape_0:.2f}%) OBS due to lack of curcial infos")
            return df 
        else:
            missing_cols = set(important_cols) - set(df.columns)
            raise Exception(f"FOLLOWING COLUMN(S) IS MISSING {missing_cols}")
        

    def clean_estimations(self, df : pd.DataFrame, liste_exceptions : List):

        important_cols = [self.name.item_result, 
                        self.name.min_estimate, 
                        self.name.max_estimate]

        if self.check_cols_exists(important_cols, df.columns):
            for col in important_cols:
                df[col] = np.where(df[col].isin(liste_exceptions), 
                                    np.nan, df[col])
                df[col] = df[col].astype(float)
            
            df[self.name.is_item_result] = 1*(df[self.name.item_result].notnull())
            df[self.name.item_result] = np.where(df[self.name.item_result].isnull(), 
                                        df[[self.name.min_estimate, self.name.max_estimate]].mean(axis=1), 
                                        df[self.name.item_result])
            return df
        else:
            missing_cols = set(important_cols) - set(df.columns)
            raise Exception(f"FOLLOWING COLUMN(S) IS MISSING {missing_cols}")
        
    
    def check_cols_exists(self, cols_a, cols_b):
        return len(set(cols_a).intersection(set(cols_b))) == len(cols_a)

    def renaming_dataframe(self, df, mapping_names):
        return df.rename(columns=mapping_names)
    