from typing import List, Dict
import pandas as pd 
import os 
import re
import numpy as np
import swifter

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from src.constants.variables import currencies
from omegaconf import DictConfig

from src.utils.utils_crawler import encode_file_name
from src.utils.utils_dataframe import (clean_useless_text,
                                       remove_lot_number,
                                       remove_dates_in_parenthesis,
                                       clean_shorten_words,
                                       remove_spaces,
                                       remove_rdv,
                                       clean_quantity,
                                       clean_dimensions)

LISTE_WORDS_REMOVE = ["--> ce lot se trouve au depot", "retrait",
                    "lot non venu", ".", "","cb",
                    "aucune désignation", "withdrawn", "pas de lot",
                    "no lot", "retiré",
                    "pas venu", "40", "lot retiré", "20", "test", 
                    "300", "non venu", "--> ce lot se trouve au depôt",
                    "hors catalogue", '()',"1 ^,,^^,,^", "estimate", "sans titre", "untitled",
                    "2 ^,,^^,,^", "3 ^,,^^,,^", "1 ^,,^", "6 ^,,^", "4 ^,,^",
                    "5 ^,,^",  ".", "", " ", ". ", 'non venu',
                    'aucune désignation', "retrait", "no lot",
                    '2 ^,,^', '3 ^,,^', '1 ^"^^"^','1 ^,,^^,,^ per dozen',
                    '5 ^,,^^,,^', '4 ^,,^^,,^','10 ^,,^^,,^',
                    "--> ce lot se trouve au depot", "pas de lot",
                    "withdrawn", "--> ce lot se trouve au depôt",
                    "pas de lot", "lot non venu"]

class TextCleaner(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)

    def get_sql_db_name(self, seller : str, mode: str = "history"):
        try:
            if mode == "history":
                return self._config.cleaning[seller].origine_table_name.history
            else:
                return self._config.cleaning[seller].origine_table_name.new
        except Exception as e:
            raise Exception(f"SELLER not found in config cleaning : {seller} - {e}")

    def get_list_element_from_text(self, variable, liste=currencies):
        return variable.apply(lambda x : re.findall(liste, str(x))[0] if 
                                             len(re.findall(liste, str(x))) > 0 else np.nan)

    def get_estimate(self, variable, min_max : str = "min"):
        def clean_thousands(x):
            return str(x).replace(" ","").replace(",","").replace("\u202f","")

        if min_max.lower() == "min":
            return variable.apply(lambda x : re.findall("\\d+", clean_thousands(x))[0] 
                                           if len(re.findall("\\d+", clean_thousands(x))) > 0 else np.nan)
        elif min_max.lower() == "max":
            return variable.apply(lambda x : re.findall("\\d+", clean_thousands(x))[1] 
                                           if len(re.findall("\\d+", clean_thousands(x))) > 1 else np.nan)
        else: 
            raise Exception("EITHER MIN OR MAX value for min_max")

    def get_splitted_infos(self, variable, index, sep='\n'):
        return  pd.DataFrame(variable.fillna("").str.split(sep).tolist(), index=index)
    
    @timing
    def clean_auctions(self, df_auctions):
        return df_auctions
    
    @timing
    def remove_missing_values(self, df, important_cols : List = []):
        
        if len(important_cols) ==0:
            important_cols = [self.name.url_full_detail,
                              self.name.item_result]

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
    def clean_id_picture(self, df : pd.DataFrame, limite : int =100, paths : Dict = {}):

        for col in [self.name.url_picture, self.name.id_picture]:
            if col not in df.columns:
                raise Exception(f"{col} not in df, cannot continue to clean {self.name.id_picture}")
            
        for col in [self.name.url_picture, self.name.id_picture]:
            df[col] = np.where(df[col].apply(lambda x: str(x) == "nan" or 
                                             str(x) == "9b2d5b4678781e53038e91ea5324530a03f27dc1d0e5f6c9bc9d493a23be9de0"), 
                                np.nan, 
                                df[col])
        
        liste_pictures_missing = df[self.name.id_picture].value_counts().loc[
            df[self.name.id_picture].value_counts() > limite].index
        self._log.info(f"SET PICTURES ID TO MISSING FOR {len(liste_pictures_missing)} picts having more than {limite} picts")
        
        df[self.name.id_picture] = np.where(df[self.name.id_picture].isnull(), "NO_PICTURE",
                                   np.where(df[self.name.id_picture].isin(list(liste_pictures_missing)), 
                                              "FAKE_PICTURE", df[self.name.id_picture]))
        
        # keep ID picture when picture is available for drouot ~2.3M
        picture_path = df[self.name.id_picture].apply(lambda x : f"{paths["pictures"]}/{x}.jpg")
        df[self.name.is_picture] = picture_path.swifter.apply(lambda x : os.path.isfile(x))

        return df
    
    @timing
    def clean_details_per_item(self, df):
        return df

    @timing
    def clean_estimations(self, df : pd.DataFrame, liste_exceptions : List = []):

        important_cols = [self.name.item_result, 
                        self.name.min_estimate, 
                        self.name.max_estimate]

        if self.check_cols_exists(important_cols, df.columns):
            for col in important_cols:
                df[col] = np.where(df[col].apply(lambda x: str(x).strip().lower()).isin(liste_exceptions), 
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
    def extract_currency(self, df):

        currency_col = self.name.brut_estimate
        if sum(df[self.name.min_estimate].isnull()) > sum(df[self.name.item_result].isnull()):
            currency_col = self.name.brut_result

        df[self.name.currency] = self.get_list_element_from_text(df[currency_col])
        df = self.filter_wrong_currency(df)
        
        if currency_col == self.name.brut_estimate and self.name.brut_result in df.columns:
            currency_brut_result = self.get_list_element_from_text(df[self.name.brut_result])
            df[self.name.currency] = np.where(df[self.name.currency].isnull(),
                                              currency_brut_result,
                                              df[self.name.currency])
            
        if currency_col == self.name.brut_result and self.name.brut_estimate in df.columns:
            currency_brut_estimate = self.get_list_element_from_text(df[self.name.brut_estimate])
            df[self.name.currency] = np.where(df[self.name.currency].isnull(),
                                              currency_brut_estimate,
                                              df[self.name.currency])
        df = self.filter_wrong_currency(df)
        
        return df
    
    def filter_wrong_currency(self, df):
        df[self.name.currency] = np.where(df[self.name.currency].str.lower().isin(["estimation : manquante",
                                                                        "this lot has been withdrawn from auction", 
                                                                        "estimate on request",
                                                                        "no result",
                                                                        "no reserve", 
                                                                        "estimate upon request", 
                                                                        "estimate unknown"]), 
                                            np.nan,
                                            df[self.name.currency])
        return df
    
    @timing
    def extract_infos(self, df):

        # drop duplicates url full detail 
        df = df.drop_duplicates(self.name.url_full_detail).reset_index(drop=True)

        for col in [self.name.item_title, self.name.item_description]:
            if col in df.columns:
                df[col] = np.where(df[col].str.lower().isin(LISTE_WORDS_REMOVE), np.nan, df[col])
            else:
                self._log.debug(f"MISSING COL {col} in df for extract infos cleaning")
        return df
        
    @timing
    def add_complementary_variables(self, df, seller):
        df[self.name.id_item] = df[self.name.url_full_detail].apply(lambda x : encode_file_name(str(x)))
        df[self.name.seller] = seller
        if seller != "drouot":
            df[self.name.house] = seller
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
    def extract_estimates(self, df):

        if self.name.brut_estimate not in df.columns and self.name.brut_result not in df.columns:
            raise Exception(f"Need to provide either {self.name.brut_estimate} or {self.name.brut_result} in the dataframe toe deduce price estimate")

        if self.name.brut_result not in df.columns:
            self._log.warning(f"{self.name.brut_result} not in df columns, will take {self.name.brut_estimate} as proxy for price estimate")
            df[self.name.brut_result] = df[self.name.brut_estimate]
            
        df[self.name.item_result] = self.get_estimate(df[self.name.brut_result], min_max="min")

        if self.name.brut_estimate not in df.columns:
            self._log.warning(f"{self.name.brut_estimate} not in df columns, will take {self.name.brut_result} as proxy for price estimate")
            df[self.name.brut_estimate] = df[self.name.brut_result]
        
        df[self.name.min_estimate] = self.get_estimate(df[self.name.brut_estimate], min_max="min")
        df[self.name.max_estimate] = self.get_estimate(df[self.name.brut_estimate], min_max="max")
        df[self.name.max_estimate] = np.where(df[self.name.max_estimate].apply(lambda x: str(x).isdigit()), 
                                        df[self.name.max_estimate], 
                                        df[self.name.min_estimate])
        return df
    
    @timing
    def concatenate_detail(self, df, df_detailed):
        return df.merge(df_detailed, how="left", on=self.name.url_full_detail, 
                        validate="1:1", suffixes=("", "_DETAIL"))
    
    @timing
    def concatenate_auctions(self, df, df_auctions):
        return df.merge(df_auctions, how="left", on=self.name.id_auction, 
                        validate="m:1", suffixes=("", "_AUCTION"))
    
    @timing
    def clean_detail_infos(self, df_detailed):
        lowered= df_detailed[self.name.detailed_description].str.strip().str.lower()
        df_detailed[self.name.detailed_description] = np.where(lowered.isin(LISTE_WORDS_REMOVE), 
                                                                np.nan,
                                                               df_detailed[self.name.detailed_description])
        if self.name.url_picture in df_detailed.columns:
            try:
                df_detailed = df_detailed.sort_values(self.name.url_picture, ascending=False)
            except Exception: # can bug if mix of string and list
                pass

        df_detailed = df_detailed.drop_duplicates(self.name.url_full_detail)
        return df_detailed
    
    @timing
    def create_unique_id(self, df):
        df = df.sort_values([self.name.url_full_detail, self.name.id_picture], ascending=[0,0])
        df[self.name.id_unique] = (df[self.name.id_item] + "_"+ df[self.name.id_picture]).apply(lambda x: encode_file_name(x))
        
        shape_0 = df.shape[0]
        df = df.drop_duplicates(self.name.id_unique)
        self._log.info(f"DROPPING {shape_0-df.shape[0]} rows due to duplicate {self.name.id_unique}")
        
        assert max(df[self.name.id_unique].value_counts()) == 1
        
        return df
    
    @timing
    def homogenize_lot_number(self, df):
        df = df.sort_values([self.name.url_auction, self.name.lot])
        df["ONE"] = 1 
        min_lot = df[[self.name.url_auction, self.name.id_item, "ONE"]].drop_duplicates()
        min_lot[self.name.lot] = min_lot[[self.name.url_auction, "ONE"]].groupby(self.name.url_auction).cumsum()
        df = df.merge(min_lot, on=[self.name.url_auction, self.name.id_item], how="left", validate="m:1", suffixes=("_ORIGIN", ""))
        return df
    
    @timing
    def clean_text_description(self, df):

        # fill title with item title first then detailed title 
        df[self.name.detailed_title] = np.where(df[self.name.item_title].isnull(),
                                                df[self.name.detailed_title],
                                                df[self.name.item_title])

        #fill description with detailed desc then item desc 
        df[self.name.total_description] = np.where(df[self.name.detailed_description].isnull(),
                                            df[self.name.item_description],
                                            df[self.name.detailed_description])
        
        # clean both
        for col in [self.name.detailed_title, self.name.total_description]:
            df[col] = df[col].swifter.apply(lambda x: self.clean_description(x))
            df[col] = np.where(df[col].isin(["None","", "nan"]), np.nan, df[col])
        return df

    def clean_description(self, x :str) -> str :
    
        x = clean_useless_text(x)
        x = remove_lot_number(x)
        x = remove_dates_in_parenthesis(x)
        x = clean_dimensions(x)
        x = clean_quantity(x)
        x = clean_shorten_words(x)
        x = remove_spaces(x)
        x = remove_rdv(x)

        return x
