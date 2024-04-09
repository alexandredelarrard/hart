import numpy as np 
import swifter
from typing import List, Dict
import pandas as pd 
pd.options.mode.copy_on_write = True

from src.context import Context
from src.utils.timing import timing

from omegaconf import DictConfig
from src.utils.utils_crawler import (read_crawled_pickles,
                                     read_json)
from src.utils.utils_extraction_gpt import (handle_answer,
                                            homogenize_keys_name,
                                            flatten_description) 
from src.utils.utils_dataframe import remove_accents
from src.modelling.transformers.GptCleaner import GPTCleaner


class StepCleanGptInference(GPTCleaner):

    def __init__(self, 
                context : Context,
                config : DictConfig):

        super().__init__(context=context, config=config)

        self.save_queue_path= self._config.gpt.save_path
        self.model_path = self._config.evaluator.model_path


    @timing
    def run(self, category="vase"):

        # get category path
        self._mapping_path = self._config.evaluator.mappings[category.lower()]

        # get col_mapping:
        self.col_mapping = read_json(self._mapping_path)

        df_done = read_crawled_pickles(path=self.save_queue_path)
        df_done = df_done.loc[df_done[self.name.category] == category.upper()]
        df_done = df_done.loc[df_done["PROMPT"].notnull()]

        df_done = self.eval_json(df_done)
        df_done = self.extract_features(df_done)
        df_done = self.remove_outliers(df_done, category)
        df_done = self.clean_features(df_done)
        df_done = self.clean_values(df_done)

        self.write_sql_data(dataframe=df_done.drop(["PROMPT", "NBR_OBJECTS", "DICT", f'IS_A_{category.upper()}'], axis=1),
                            table_name=f"TEST_0.05_CLEAN_{category.upper()}",
                            if_exists="replace")

        return df_done

    @timing
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

    @timing
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
                                                "nan", "undefined",
                                                'non specified', 'not applicable', 'non specificato']), np.nan,
                                                df_done[col.upper()])
    
        return df_done

    @timing
    def remove_outliers(self, df_done, category):

        shape_0 = df_done.shape[0]

        df_done["NUMBER_DESCRIBED_OBJECTS"] = df_done["NUMBER_DESCRIBED_OBJECTS"].fillna("1")
        df_done = df_done.loc[df_done["NUMBER_DESCRIBED_OBJECTS"].isin(["1", "2", "3", "4", "5"])]
        
        df_done = df_done.loc[df_done["OBJECT_CATEGORY"].notnull()]
        df_done = df_done.loc[df_done[f"IS_A_{category.upper()}"].isin(["true", "True"])]

        self._log.info(f"FILTERING {shape_0 - df_done.shape[0]} ({(shape_0 - df_done.shape[0])*100/shape_0:.1f}%) due to lack of info / mismatch")

        return df_done

    @timing
    def clean_features(self, df_done):
        
        df_done["VASE_HEIGHT"] = df_done["VASE_HEIGHT"].apply(lambda x: self.handle_cm(str(x)))
        df_done["VASE_SHAPE"] = df_done["VASE_SHAPE"].apply(lambda x : self.map_value_to_key(x, self.shape_mapping))
        df_done["VASE_COUNTRY"] = df_done["VASE_COUNTRY"].apply(lambda x : self.map_value_to_key(x, self.country_mapping))

        # deduce color
        vase_color = df_done["VASE_COLOR"].apply(lambda x : self.map_value_to_key(x, self.color_mapping))
        df_done["VASE_COLOR"] = np.where(vase_color.isnull(),
                                           df_done["VASE_MATERIAL"].apply(lambda x : self.map_value_to_key(x, self.color_mapping)),
                                          vase_color)
       
        # deduce material
        vase_material = df_done["VASE_MATERIAL"].apply(lambda x : self.map_value_to_key(x, self.material_mapping))
        df_done["VASE_MATERIAL"] = np.where(vase_material.isnull(),
                                           vase_color.apply(lambda x : self.map_value_to_key(x, self.material_mapping)),
                                           vase_material)
        
        # get style
        df_done["VASE_STYLE"] = df_done["VASE_PERIODE_OR_CIRCA_YEAR"].apply(lambda x: self.map_value_to_key(x, self.style_mapping))
        df_done["VASE_STYLE"] = np.where(df_done["VASE_STYLE"].isnull(),
                                        df_done["VASE_SIGNED"].apply(lambda x: self.map_value_to_key(x, self.style_mapping)),
                                        df_done["VASE_STYLE"])
        
        # deduce year
        df_done["VASE_YEAR"] = df_done["VASE_PERIODE_OR_CIRCA_YEAR"].apply(lambda x: self.clean_periode(x))
        df_done["VASE_YEAR"] = np.where(df_done["VASE_YEAR"].isnull(),
                                        df_done["VASE_PERIODE_OR_CIRCA_YEAR"].apply(lambda x: self.map_value_to_key(x, self.period_mapping)),
                                        df_done["VASE_YEAR"])

        df_done["VASE_SIGNED"] = np.where(df_done["VASE_SIGNED"].isnull()|df_done["VASE_SIGNED"].isin(["not marked", "non signe", 
                                                                                                       "not signed", "no", "false", 
                                                                                                       "unmarked"]), 
                                            False, True)
        
        # conditions cleaning 
        # TODO: model qui prédit létat à partir du texte- score allant de 0 a 5
        df_done["VASE_CONDITION"] = df_done["VASE_CONDITION"].apply(lambda x : self.map_value_to_key(x, self.condition_mapping))

        # decorations cleaning
        df_done["VASE_DECORATIONS"] = df_done["VASE_DECORATIONS"].apply(lambda x : self.map_value_to_key(x, self.decorations_mapping))

        return df_done
    
    @timing
    def clean_values(self, df_done):
        for col in ["VASE_HEIGHT", "VASE_YEAR", "NUMBER_DESCRIBED_OBJECTS"]:
            df_done[col] = df_done[col].apply(lambda x: self.eval_number(str(x)))

        #relation d'ordre sur la condition du vase
        df_done["VASE_CONDITION"] = df_done["VASE_CONDITION"].map({"very good": 4,
                                                                    "good_": 3,
                                                                    "okay_": 2,
                                                                    "poor": 1})
        # to be able to save into sql 
        df_done["ANSWER"] = df_done["ANSWER"].astype(str)

        return df_done
    
    def get_all_keys(self, df_done):
        
        def element_cleaner(x):
            x = remove_accents(x.lower()).strip()
            x = x.replace(" ", "_")
            return x
        
        all_keys = [element_cleaner(element) for dico in df_done["ANSWER"].tolist() 
                    for element in dico.keys()]

        value_counts = pd.Series(all_keys).value_counts()
        return value_counts