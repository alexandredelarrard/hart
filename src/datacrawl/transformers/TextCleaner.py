from typing import List
import pandas as pd 

import re
import numpy as np
from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from src.constants.variables import currencies
from omegaconf import DictConfig

from src.utils.utils_crawler import encode_file_name

class TextCleaner(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)

    def get_sql_db_name(self, seller : str):
        try:
            return self._config.cleaning[seller].origine_table_name
        except Exception as e:
            raise Exception(f"SELLER not found in config embedding_history : {seller} - {e}")

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
    
    @timing
    def remove_missing_values(self, df, important_cols : List = []):
        
        if len(important_cols) ==0:
            important_cols = [self.name.url_full_detail, 
                              self.name.item_infos]

        if self.check_cols_exists(important_cols, df.columns):
            shape_0 = df.shape[0]
            for i, col in enumerate(important_cols):
                if i == 0:
                    filter_missing = df[col].notnull()
                else:
                    filter_missing = (filter_missing)*(df[col].notnull())

            df = df.loc[filter_missing].reset_index(drop=True) 
            shape_1 = df.shape[0]
            self._log.info(f"REMOVING {shape_0 - shape_1} \
                        ({(shape_0-shape_1)*100/shape_0:.2f}%) OBS due to lack of curcial infos")
            
            return df 
        else:
            missing_cols = set(important_cols) - set(df.columns)
            raise Exception(f"FOLLOWING COLUMN(S) IS MISSING {missing_cols}")
        
    @timing
    def clean_id_picture(self, df : pd.DataFrame, limite : int =100):
        liste_pictures_missing = df[self.name.id_picture].value_counts().loc[
            df[self.name.id_picture].value_counts() > limite].index
        self._log.info(f"SET PICTURES ID TO MISSING FOR {len(liste_pictures_missing)} picts having more than {limite} picts")
        
        df[self.name.id_picture] = np.where(df[self.name.id_picture].isin(list(liste_pictures_missing)), 
                                                np.nan, df[self.name.id_picture])
        return df

    @timing
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
        
    @timing
    def add_complementary_variables(self, df, seller):
        df[self.name.id_item] = df[self.name.url_full_detail].apply(lambda x : encode_file_name(str(x)))
        df[self.name.seller] = seller
        return df

    def check_cols_exists(self, cols_a, cols_b):
        return len(set(cols_a).intersection(set(cols_b))) == len(cols_a)

    def renaming_dataframe(self, df, mapping_names):
        return df.rename(columns=mapping_names)
    
    @timing
    def remove_features(self, df, list_features):
        to_drop = set(list_features).intersection(df.columns)
        if len(to_drop) == len(list_features):
            df = df.drop(list_features, axis=1)
        else:
            missing = set(list_features) - set(to_drop)
            self._log.warning(f"CANNOT DROP {missing} : column MISSING")
            df = df.drop(list(to_drop), axis=1)
        return df
    
    @timing
    def concatenate_detail(self, df, df_detailed):
        return df.merge(df_detailed, how="left", on=self.name.url_full_detail, 
                        validate="1:1", suffixes=("", "_DETAIL"))
    
    @timing
    def clean_detail_infos(self, df_detailed):
        lowered= df_detailed[self.name.detailed_description].str.lower()
        df_detailed[self.name.detailed_description] = np.where(lowered.isin(["retiré", ".", "", " ", 'lot non venu', 'non venu',
                                                                            'aucune désignation', "retrait", "no lot",
                                                                            "--> ce lot se trouve au depot", "pas de lot",
                                                                            "withdrawn", "--> ce lot se trouve au depôt",
                                                                            "pas de lot", "lot non venu", ""]), 
                                                                np.nan,
                                                               df_detailed[self.name.detailed_description])
        df_detailed = df_detailed.drop_duplicates([self.name.url_full_detail])
        return df_detailed
    
    def remove_dates_in_parenthesis(self, x):
        pattern = re.compile(r'\([0-9-]+\)')
        return re.sub(pattern, '',  x)

    def clean_dimensions(self, x):
        pattern = re.compile(r"(\d+.?\d+[ xX]+\d+.?\d+)")
        origin = re.findall(pattern, x)
        if len(origin) == 1:
            origin = origin[0]
            numbers = origin.lower().split("x")
            if len(numbers) == 2:
                new = f" longueur: {numbers[0].strip()} largeur: {numbers[1].strip()}"
                return x.replace(origin, new)
        return x 
    
    def clean_hight(self, x):
        x = re.sub(r"(H[\s.:])[\s.:\d+]", " hauteur ", x, flags=re.I)
        x = re.sub(r"(L[\s.:])[\s.:\d+]", " longueur ", x, flags=re.I)
        x = re.sub(r"(Q[\s.:])[\s.:\d+]", " quantite ", x, flags=re.I)
        x = re.sub(" g. ", " gramme ", x, flags=re.I)
        x = re.sub(" gr. ", " gramme ", x, flags=re.I)
        return x
    
    def clean_shorten_words(self, x):
        x = re.sub(r"[\s\d+\s](B)\s", " bouteille ", x, flags=re.I, count=1)
        x = re.sub(" bout. ", " bouteille ", x, flags=re.I, count=1)
        x = re.sub(" bt. ", " bouteille ", x, flags=re.I, count=1)
        x = re.sub("@", "a", x)
        x = re.sub("n°", " numéro ", x)
        x = re.sub(" in. ", " inch ", x, flags=re.I)
        x = re.sub(" ft. ", " feet ", x, flags=re.I)
        x = re.sub(" approx. ", " approximativement ", x)
        return x
    
    def remove_spaces(self, x):
        x = str(x).strip()
        x = re.sub(" +", " ", x)
        return x
    
    def remove_lot_number(self, x):
        return re.sub(r"^(\d+\. )", '', str(x))
    
    def remove_estimate(self, x):
        return str(x).split("\nEstimate")[0]
    