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
                                            homogenize_keys_name) 
from src.utils.utils_dataframe import remove_accents
from src.dataclean.transformers.GptCleaner import GPTCleaner
from src.modelling.transformers.NlpToolBox import NLPToolBox

class StepCleanGptInference(GPTCleaner):

    def __init__(self, 
                context : Context,
                config : DictConfig,
                category: str = "painting"):

        super().__init__(context=context, config=config)

        self.category= category.upper()
        self.save_queue_path= "/".join([self._config.gpt.save_path, category])
        self.clean_info_with_mapping = self._config.evaluator.info_to_mapping
        self.mappings = self._config.evaluator.cleaning_mapping
        self.cols_to_cm = self._config.evaluator.handle_cm
        self.cols_to_date = self._config.evaluator.handle_dates
        self.cols_to_float = self._config.evaluator.cols_to_float
        self.binary_cols = self._config.evaluator.binary_cols

        self.nlp = NLPToolBox()

    @timing
    def run(self):

        # get category path
        self._mapping_path = self._config.evaluator.mappings[self.category.lower()]

        # get col_mapping:
        self.col_mapping = read_json(self._mapping_path)
        self.cat_map = read_json(r"D:\data\llm_extracts\features_to_extract\object_category_mapping.json")

        df_done = read_crawled_pickles(path=self.save_queue_path)
        df_names = self.read_sql_data("ARTISTS_DB_PRICE")

        a = df_done.loc[df_done["NUMBER_OBJECTS_DESCRIBED"].isin(["1", "2", "3"])]
        b = a["OBJECT_CATEGORY"].value_counts()
        c = b.loc[~b.index.isin([x for liste in self.cat_map.values() for x in liste])]
        print((c.sum()+df_done.shape[0] - b.sum())/b.sum())

        df_done = self.eval_json(df_done)
        df_done = self.extract_features(df_done)
        df_done = self.remove_outliers(df_done)
        df_done = self.clean_dimensions(df_done)
        df_done = self.clean_dates(df_done)
        df_done = self.clean_text(df_done)
        df_done = self.clean_binary(df_done)
        df_done = self.clean_values(df_done)
        df_done = self.clean_names(df_done)

        self.save_infos_to_tables(df_done)

    
    def save_infos_to_tables(self, df_done):

        # save a table mapping desc to specific category 
        # any status KO will have to be redone with proper prompt
        df_cat = df_done[[self.name.id_item, self.name.category, "NUMBER_OBJECTS_DESCRIBED"]]
        df_cat["STATUS"] = np.where(df_cat["CLEAN_" + self.name.category] == self.category.lower(), "OK", "KO")
        self.remove_rows_sql_data(values=df_cat[self.name.id_item].tolist(),
                                    column=self.name.id_item,
                                    table_name="CATEGORY_MAPPING_GPT")
        self.write_sql_data(dataframe=df_cat,
                            table_name="CATEGORY_MAPPING_GPT",
                            if_exists="append")
        
        # save the ones of proper category mapped to right prompt
        sub_df = df_done.loc[df_done["CLEAN_" + self.name.category] == self.category.lower()]
        self.remove_rows_sql_data(values=sub_df[self.name.id_item].tolist(),
                                column=self.name.id_item,
                                table_name=f"GPT_FEATURES_{self.category}")
        self.write_sql_data(dataframe=sub_df,
                            table_name=f"GPT_FEATURES_{self.category}",
                            if_exists="append")

    @timing
    def eval_json(self, df_done):

        # evaluate string to Dict or List
        df_done["ANSWER"] = df_done[[self.name.id_item, "ANSWER"]].apply(lambda x : handle_answer(x), axis=1)
        df_done = df_done.loc[(df_done["ANSWER"] != "{}")&(df_done["ANSWER"].notnull())]
        
        # remove lots of too many different objects
        nbr_objects = df_done["ANSWER"].apply(lambda x: len(x) if isinstance(x, List) else 1)
        self._log.info(nbr_objects.value_counts())
        df_done = df_done.loc[3>=nbr_objects]

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
        
        # clean dict 
        df_done["ANSWER"] = df_done["ANSWER"].swifter.apply(lambda x: 
                                            homogenize_keys_name(x, self.col_mapping))
        
        for col in self.col_mapping.keys():
            df_done[col.upper()] = df_done["ANSWER"].str.get(col)
            df_done[col.upper()] = df_done[col.upper()].apply(lambda x: ", ".join(x) if isinstance(x, List) else x)
            df_done[col.upper()] = np.where(df_done[col.upper()].isin(["n/a", "unspecified", "", "unknown", 
                                                "none", 'not specified', "'n/a'", "null", "not found", 'na',
                                                "nan", "undefined", "Null", " ",
                                                'non specified', 'not applicable', 'non specificato']), np.nan,
                                                df_done[col.upper()])
        return df_done

    @timing
    def remove_outliers(self, df_done):

        shape_0 = df_done.shape[0]
        df_done["NUMBER_OBJECTS_DESCRIBED"] = df_done["NUMBER_OBJECTS_DESCRIBED"].fillna("1")
        df_done = df_done.loc[df_done["NUMBER_OBJECTS_DESCRIBED"].isin(['0', "1", "2", "3"])]
        self._log.info(f"FILTERING {shape_0 - df_done.shape[0]} ({(shape_0 - df_done.shape[0])*100/shape_0:.1f}%) due to lack of info / mismatch")

        df_done = df_done.reset_index(drop=True)
        return df_done
    
    def apply_mapping_func(self, vector, mapping_dict):
        return vector.swifter.apply(lambda x: self.map_value_to_key(str(x).replace("\"-\"", "\" \"").replace("\",\"","\"\""), mapping_dict))
    
    @timing
    def clean_dimensions(self, df_done):
        df_columns = df_done.columns
        for column in self.cols_to_cm:
            column = self.col_names_with_category(column)
            if column in df_columns:
                df_done[column] = df_done[column].apply(lambda x: self.handle_cm(str(x)))
        return df_done

    @timing
    def clean_dates(self, df_done):
        df_columns = df_done.columns
        for column in self.cols_to_date:
            column = self.col_names_with_category(column)
            if column in df_columns:
                df_done[column] = df_done[column].apply(lambda x: self.clean_periode(str(x)))
        return df_done
    
    @timing
    def clean_text(self, df_done):
        df_columns = df_done.columns
        for function_mapping, column_to_clean in self.clean_info_with_mapping.items():
            for target_column, columns_name in column_to_clean.items():
                if len(columns_name) == 1:
                    col_name = self.col_names_with_category(target_column)

                    if col_name in df_columns:
                        self._log.info(f"CLEANING {target_column}")

                        mapping_dict = self.order_mapping_dict(self.mappings[function_mapping])
                        df_done["CLEAN_"+col_name] = self.apply_mapping_func(df_done[col_name], mapping_dict)
                else:
                    col_name = self.col_names_with_category(target_column)

                    if col_name in df_columns:
                        self._log.info(f"CLEANING {target_column}")

                        mapping_dict = self.order_mapping_dict(self.mappings[function_mapping])
                        df_done["CLEAN_"+ col_name] = self.apply_mapping_func(df_done[col_name], mapping_dict)
                        
                        for other_col_name in columns_name[1:]:
                            other_col_name = self.col_names_with_category(other_col_name)
                            df_done["CLEAN_"+ col_name] = np.where(df_done["CLEAN_"+ col_name].isnull(),
                                                                self.apply_mapping_func(df_done[other_col_name], mapping_dict),
                                                                df_done["CLEAN_"+col_name])
        return df_done
    
    @timing
    def clean_binary(self, df_done):
        df_columns = df_done.columns
        for column in self.binary_cols:
            column = self.col_names_with_category(column)
            if column in df_columns:
                df_done[column] = np.where(df_done[column].isin(["not marked", "non signe", "non signee",
                                            "not signed", "no", "false", "not dated", "not", "non", "faux",
                                            "unmarked"]), False,
                                  np.where(df_done[column].isnull()|df_done[column].isin(["none", "null", "nan"]), np.nan, True))
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
    
    def col_names_with_category(self, col_name):
        if col_name[0] == "_":
            return self.category + col_name
        return col_name
    
    def order_mapping_dict(self, mapping_dict):
        ordered_mapping_dict = {}
        for k in sorted(mapping_dict, key=len, reverse=True):
            ordered_mapping_dict[k] = mapping_dict[k]
        return ordered_mapping_dict

    #### FOR CHECKS
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
            if col in df_done.columns:
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