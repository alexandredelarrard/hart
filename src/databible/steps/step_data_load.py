import os
import time
import random
from typing import List
from omegaconf import DictConfig
import pandas as pd

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.utils.utils_dataframe import homogenize_columns

class StepDataLoad(Step):
    
    def __init__(self,
                 config : DictConfig, 
                 context : Context):

        super().__init__(context=context, config=config)


    @timing
    def run(self):

        # initialize the drivers 
        data_dict = self.load_datas()

        # clean datas 
        data_dict = self.pre_clean_data(data_dict)

        return data_dict


    @timing
    def load_datas(self):

        data_dict= {}

        for granularity, data_name in self._config.flat_file.insee.items():
            data_dict[granularity] = {}
            
            for data_name, values in self._config.flat_file.insee[granularity].items():
                data_dict[granularity][data_name] = self.load_data(values.path, values.sep)

                if "table_name" not in values.keys():
                    values.table_name = "_".join([granularity.upper(), data_name.upper()])

                if values.table_name not in self._sql_table_names:
                    data_dict[granularity][data_name].to_sql(values.table_name, 
                                                             con=self._context.db_con)

        return data_dict


    def load_data(self, data_path, sep):
        df = pd.read_csv(data_path, sep=sep, on_bad_lines='warn')
        df.columns = homogenize_columns(df.columns)
        return df


    @timing
    def pre_clean_data(self, data_dict):

        cleaning_methods = [method for method in dir(StepDataLoad) if "cleaning"  in method]
    
        for methode in cleaning_methods:
            data_dict = eval(f"self.{methode}")(data_dict)

        return data_dict

    @timing
    def cleaning_commune_code_geo(self, data_dict):
        data_dict["commune"]["communes_encodage_2020"] = data_dict["commune"]["communes_encodage_2020"].drop_duplicates("COM")
        return data_dict

    @timing
    def cleaning_carreaux_200m(self, data_dict):

        df = data_dict["carreaux_200m"]["met"].copy()
        
        # split insee code to have carreaux per insee code 
        df["LCOG_GEO"] = df["LCOG_GEO"].apply(lambda x : [str(x)[i:i+5] for i in range(0, len(str(x)), 5) ])
        df = df.explode("LCOG_GEO")

        data_dict["carreaux_200m"]["met"] = df

        return data_dict
