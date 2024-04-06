import numpy as np 
import swifter
from typing import List, Dict
import pandas as pd 
pd.options.mode.copy_on_write = True

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from omegaconf import DictConfig
from src.utils.utils_crawler import (read_crawled_pickles,
                                     read_json)
from src.utils.utils_extraction_gpt import (handle_answer,
                                            homogenize_keys_name,
                                            flatten_description) 
from src.utils.utils_dataframe import remove_accents


class StepCleanGptInference(Step):

    def __init__(self, 
                context : Context,
                config : DictConfig):

        super().__init__(context=context, config=config)

        self.save_queue_path= self._config.gpt.save_path
        self.model_path = self._config.evaluator.model_path
        self.watch_col_mapping_path = self._config.evaluator.watch_features_mapping

    @timing
    def run(self):

        # get col_mapping:
        self.col_mapping = read_json(self.watch_col_mapping_path)

        df_done = read_crawled_pickles(path=self.save_queue_path)
        df_done = self.clean_answer(df_done)
        df_done = self.eval_json(df_done)
        df_done = self.extract_features(df_done)
        df_done = self.clean_features(df_done)

        return df_done


    def clean_answer(self, df_done):
        df_done[self.name.total_description] = df_done[self.name.total_description].str.get("content")
        df_done[self.name.total_description] = df_done[self.name.total_description].apply(lambda x: x.split("description:")[-1])
        return df_done


    def eval_json(self, df_done):

        # evaluate string to Dict or List
        df_done["ANSWER"] = df_done["ANSWER"].apply(lambda x : handle_answer(x))
        df_done = df_done.loc[(df_done["ANSWER"] != "{}")&(df_done["ANSWER"].notnull())]
        
        # remove lots of too many different objects
        df_done["NBR_OBJECTS"] = df_done["ANSWER"].apply(lambda x: len(x) if isinstance(x, List) else 1)
        df_done = df_done.loc[1>=df_done["NBR_OBJECTS"]]

        # align multi objects with simple objects by exploding desc and keep thos existing
        df_done["ANSWER"] = df_done["ANSWER"].apply(lambda x: [x] if isinstance(x, Dict) else x)
        df_done = df_done.explode("ANSWER")
        df_done["DICT"] =  df_done["ANSWER"].apply(lambda x: isinstance(x, Dict))
        df_done = df_done.loc[df_done["DICT"]]

        return df_done


    def extract_features(self, df_done):

        # handle features element
        df_done = df_done.loc[df_done["ANSWER"].notnull()]
        df_done["ANSWER"] = df_done["ANSWER"].swifter.apply(lambda x: 
                                            flatten_description(x))
        
        # clean dict 
        df_done["ANSWER"] = df_done["ANSWER"].swifter.apply(lambda x: 
                                            homogenize_keys_name(x, self.col_mapping))
        
        for col in self.col_mapping.keys():
            df_done[col.upper()] = df_done["ANSWER"].str.get(col)
            df_done[col.upper()] = np.where(df_done[col.upper()].isin(["n/a", "unspecified", "", "unknown", 
                                                "none", 'not specified', "'n/a'", "null", "not found", 'na',
                                                'non specified', 'not applicable', 'non specificato']), np.nan,
                                                df_done[col.upper()])
    
        return df_done


    def clean_features(self, df_done):
        return df_done

    def get_all_keys(self, df_done):
        
        def element_cleaner(x):
            x = remove_accents(x.lower()).strip()
            x = x.replace(" ", "_")
            return x
        
        all_keys = [element_cleaner(element) for dico in df_done["ANSWER"].tolist() 
                    for element in dico.keys()]

        value_counts = pd.Series(all_keys).value_counts()
        value_counts.to_csv("./data/default//watch_keys.csv")