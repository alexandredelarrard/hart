import os
import time
import random
from typing import List, Dict
from omegaconf import DictConfig
import pandas as pd

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.utils.utils_dataframe import homogenize_columns, transform_types

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
            
            for data_name, data_config in self._config.flat_file.insee[granularity].items():
                data_dict[granularity][data_name] = self.load_data(data_config=data_config,
                                                                   names=self._config.naming[granularity][data_name],
                                                                   dtypes=self._config.dtypes[granularity][data_name])

                if "table_name" not in data_config.keys():
                    data_config.table_name = "_".join([granularity.upper(), data_name.upper()])

                self.write_sql_data(dataframe=data_dict[granularity][data_name],
                                    table_name=data_config.table_name)

        return data_dict


    def load_data(self, data_config, 
                        names : List  = None, 
                        dtypes : Dict = None):

        kwargs = {}
        if "na_values" in data_config.keys():
            kwargs["na_values"] = data_config.na_values

        if dtypes:
            kwargs["dtype"] = dict(dtypes)
 
        try:
            df = pd.read_csv(data_config.path, 
                            sep=data_config.sep, 
                            on_bad_lines='warn', 
                            header=0,
                            **kwargs)
            df.columns = homogenize_columns(list(names.values()))

        except Exception as e:
            raise Exception(f"Could not read data {data_config['table_name']}", e)
        
        self._log.info(f"Read csv file {data_config.table_name} done")
        
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
