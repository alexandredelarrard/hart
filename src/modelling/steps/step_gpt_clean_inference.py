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
from src.modelling.transformers.NlpToolBox import NLPToolBox


class StepCleanGptInference(GPTCleaner):

    def __init__(self, 
                context : Context,
                config : DictConfig):

        super().__init__(context=context, config=config)

        self.save_queue_path= self._config.gpt.save_path
        self.model_path = self._config.evaluator.model_path
        self.clean_info_with_mapping = self._config.evaluator.info_to_mapping
        self.cols_to_cm = self._config.evaluator.handle_cm
        self.cols_to_date = self._config.evaluator.handle_cm
        self.cols_to_float = self._config.evaluator.handle_cm

        self.nlp = NLPToolBox()

    @timing
    def run(self, category="all"):

        category="all"
        self.category= category.upper()

        # get category path
        self._mapping_path = self._config.evaluator.mappings[category.lower()]

        # get col_mapping:
        self.col_mapping = read_json(self._mapping_path)

        df_done = read_crawled_pickles(path=self.save_queue_path)
        df_done = df_done.loc[df_done[self.name.category] == category.upper()]
        df_done = df_done.loc[df_done["PROMPT"].notnull()]

        df_done = self.eval_json(df_done)
        df_done = self.extract_features(df_done)
        self.homogenize_answers(df_done)

        df_done = self.remove_outliers(df_done)
        df_done = self.clean_features(df_done)
        df_done = self.clean_values(df_done)

        self.write_sql_data(dataframe=df_done.drop(["PROMPT"], axis=1),
                            table_name=f"TEST_0.05_CLEAN_{category.upper()}",
                            if_exists="replace")

        return df_done

    @timing
    def eval_json(self, df_done):

        # evaluate string to Dict or List
        df_done["ANSWER"] = df_done[["ID_ITEM", "ANSWER"]].apply(lambda x : handle_answer(x), axis=1)
        df_done = df_done.loc[(df_done["ANSWER"] != "{}")&(df_done["ANSWER"].notnull())]
        
        # remove lots of too many different objects
        nbr_objects = df_done["ANSWER"].apply(lambda x: len(x) if isinstance(x, List) else 1)
        df_done = df_done.loc[1>=nbr_objects]

        # align multi objects with simple objects by exploding desc and keep thos existing
        df_done["ANSWER"] = df_done["ANSWER"].apply(lambda x: [x] if isinstance(x, Dict) else x)
        df_done = df_done.explode("ANSWER")

        # remove non dict answers since we asked for a JSON format
        is_dict =  df_done["ANSWER"].apply(lambda x: isinstance(x, Dict))
        df_done = df_done.loc[is_dict]

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
                                                "nan", "undefined", "Null",
                                                'non specified', 'not applicable', 'non specificato']), np.nan,
                                                df_done[col.upper()])
    
        return df_done

    @timing
    def remove_outliers(self, df_done):

        shape_0 = df_done.shape[0]

        df_done["NUMBER_OBJECTS_DESCRIBED"] = df_done["NUMBER_OBJECTS_DESCRIBED"].fillna("1")
        df_done = df_done.loc[df_done["NUMBER_OBJECTS_DESCRIBED"].isin(["1", "2"])]
        df_done = df_done.loc[df_done["OBJECT_CATEGORY"].notnull()]

        self._log.info(f"FILTERING {shape_0 - df_done.shape[0]} ({(shape_0 - df_done.shape[0])*100/shape_0:.1f}%) due to lack of info / mismatch")

        return df_done
    
    def apply_mapping_func(self, vector, function_mapping):
        return vector.apply(lambda x: eval(f"self.map_value_to_key(str(x).replace(\"-\",\" \").replace(\",\",\"\"), self.{function_mapping})"))

    @timing
    def clean_features(self, df_done):

        df_columns = df_done.columns

        for column in self.cols_to_cm:
            if column in df_columns:
                df_done[f"{self.category}" + column] = df_done[f"{self.category}" + column].apply(lambda x: self.handle_cm(str(x)))

        for column in self.cols_to_date:
            if column in df_columns:
                df_done[f"{self.category}" + column] = df_done[f"{self.category}" + column].apply(lambda x: self.clean_periode(str(x)))
        
        for function_mapping, columns_name in self.clean_info_with_mapping.items():
            if len(columns_name) == 1:
                col_name = columns_name[0]
                if col_name in df_columns:
                    df_done[f"{self.category}" + col_name] = self.apply_mapping_func(df_done[f"{self.category}" + col_name], function_mapping)
            else:
                col_name = columns_name[0]
                if col_name in df_columns:
                    df_done[f"{self.category}" + col_name] = self.apply_mapping_func(df_done[f"{self.category}" + col_name], function_mapping)
                    for other_col_name in columns_name[1:]:
                        df_done[f"{self.category}" + col_name] = np.where(df_done[f"{self.category}" + col_name].isnull(),
                                                    self.apply_mapping_func(df_done[f"{self.category}" + other_col_name], function_mapping),
                                                    df_done[f"{self.category}" + col_name])

        if f"{self.category}_SIGNED" in df_done.columns:
            df_done[f"{self.category}_SIGNED"] = np.where(df_done[f"{self.category}_SIGNED"].isnull()|df_done[f"{self.category}_SIGNED"].isin(
                                                                    ["not marked", "non signe", 
                                                                    "not signed", "no", "false", 
                                                                    "unmarked"]), 
                                                False, True)

        return df_done
    
    @timing
    def clean_values(self, df_done):
        for col in self.cols_to_float:
            if col in df_done.columns:
                df_done[col] = df_done[col].apply(lambda x: self.eval_number(str(x)))

        #relation d'ordre sur la condition de l'objet
        if f"{self.category}_CONDITION" in df_done.columns:
            df_done[f"{self.category}_CONDITION"] = df_done[f"{self.category}_CONDITION"].map({"very good": 4,
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
     
    def homogenize_answers(self, df_done):

        for col in ["OBJECT_CATEGORY", "OBJECT_SUB_CATEGORY"]:
            df_done[col] = df_done[col].str.lower()
            df_done[col] = df_done[col].swifter.apply(lambda x: self.nlp.stemSentence(str(x).split(" ")))

        df_done["CLASSE"] = np.where(df_done["OBJECT_CATEGORY"].isin(["jewelri", "jewelleri", "furnitur",
                                                                      "silver", "objet d'art", "decor art", "sculptur", "print",
                                                                      "textil", "mobili", "accessori",
                                                                      "cloth", "ceramiqu", "meubl", "ceram", 
                                                                      "art", "artwork", "porcelain", "fashion",
                                                                      "potteri", "decor object", "object", 
                                                                      "fine art", "mix media", "collect",
                                                                      "ornament", "object of vertu", "furnitur and decor art",
                                                                      "meubl ancien et de style", "art decoratif", "object d'art", 
                                                                      "art de la tabl", "jewel", "mobili & objet d'art",
                                                                      "scientif instrument", "decor art",
                                                                      "silverwar", "tablewar", "vessel", "militaria","glassware",
                                                                      "contemporari art","arm", "music instrument", "sculptur", "ceram",
                                                                      "metalwork", "work of art", "record", "model", "jewelri", "porcelain",
                                                                      "decor object", "metalwar", "ornament", "silver jewelri", "ceramiqu", 
                                                                      "weapon", "tablewar", "miniatur", "sculptur"]), 
                                     df_done["OBJECT_SUB_CATEGORY"],
                                     df_done["OBJECT_CATEGORY"])
        
        value_counts = df_done["CLASSE"].value_counts()
        sub_cat = read_json("D:/data/default/category_features_stem.json")
        values = [x for xs in sub_cat.values() for x in xs] 
        value_counts = value_counts.loc[~value_counts.index.isin(values)]
        value_counts.loc[value_counts != 1].to_csv("D:/data/default/sub_cat_value_counts.csv", sep=";")