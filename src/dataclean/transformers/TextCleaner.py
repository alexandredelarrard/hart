from typing import List
import pandas as pd 
import os 
import re
import numpy as np

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from src.constants.variables import currencies
from omegaconf import DictConfig

from src.utils.utils_crawler import encode_file_name

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
        self.root_path = self._config.crawling.root_path

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
        if min_max.lower() == "min":
            return variable.apply(lambda x : re.findall(r"\d+", str(x).replace(" ","").replace(",",""))[0] 
                                           if len(re.findall(r"\d+", str(x).replace(" ","").replace(",",""))) > 0 else np.nan)
        elif min_max.lower() == "max":
            return variable.apply(lambda x : re.findall(r"\d+", str(x).replace(" ","").replace(",",""))[1] 
                                           if len(re.findall(r"\d+", str(x).replace(" ","").replace(",",""))) > 1 else np.nan)
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
    def clean_id_picture(self, df : pd.DataFrame, limite : int =100, seller : str = "drouot"):

        if self.name.url_picture not in df.columns:
            raise Exception(f"{self.name.url_picture} not in df, cannot continue to clean {self.name.id_picture}")
        
        if self.name.id_picture not in df.columns:
            df[self.name.id_picture] = df[self.name.url_picture].swifter.apply(lambda x: os.path.basename(str(x)))

        liste_pictures_missing = df[self.name.id_picture].value_counts().loc[
            df[self.name.id_picture].value_counts() > limite].index
        self._log.info(f"SET PICTURES ID TO MISSING FOR {len(liste_pictures_missing)} picts having more than {limite} picts")
        
        df[self.name.id_picture] = np.where(df[self.name.id_picture].isnull(), "NO_PICTURE",
                                   np.where(df[self.name.id_picture].isin(list(liste_pictures_missing)), 
                                              "FAKE_PICTURE", df[self.name.id_picture]))
        
        # keep ID picture when picture is available for drouot ~2.3M
        picture_path = df[self.name.id_picture].apply(lambda x : f"{self.root_path}/{seller}/pictures/{x}.jpg")
        df[self.name.is_picture] = picture_path.swifter.apply(lambda x : os.path.isfile(x))

        return df
    
    @timing
    def clean_details_per_item(self, df):
        return df

    @timing
    def clean_estimations(self, df : pd.DataFrame, liste_exceptions : List):

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

        currency_brut_estimate = self.get_list_element_from_text(df[currency_col])
        df[self.name.currency] = np.where(currency_brut_estimate.str.lower().isin(["estimation : manquante",
                                                                        "this lot has been withdrawn from auction", 
                                                                        "estimate on request",
                                                                        "no reserve", 
                                                                        "estimate upon request", 
                                                                        "estimate unknown"]), 
                                            np.nan,
                                            currency_brut_estimate)
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
            df_detailed = df_detailed.sort_values(self.name.url_picture)
            
        df_detailed = df_detailed.drop_duplicates(self.name.url_full_detail)
        return df_detailed
    
    @timing
    def create_unique_id(self, df):
        df = df.sort_values([self.name.url_full_detail, self.name.id_picture], ascending=[0,0])
        df = df.drop_duplicates(self.name.url_full_detail)
        df[self.name.id_unique] = (df[self.name.id_item] + "_"+ df[self.name.id_picture]).apply(lambda x: encode_file_name(x))
        assert max(df[self.name.id_unique].value_counts()) == 1
        return df
    
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
        x = re.sub(" g. ", " gramme ", x, flags=re.I)
        x = re.sub(" gr. ", " gramme ", x, flags=re.I)
        x = re.sub(" diam. ", " diametre ", x, flags=re.I)
        x = x.replace("Photo non contractuelle", "")
        x = x.replace("Pour enchérir, veuillez consulter la section « Informations de vente »", "")

        return x
    
    def remove_spaces(self, x):
        x = str(x).strip()
        x = re.sub(" +", " ", x)
        return x
    
    def remove_lot_number(self, x):
        return re.sub(r"^(\d+\. )", '', str(x))
    
    def remove_estimate(self, x):
        return str(x).split("\nEstimate")[0]
    
    def remove_rdv(self, x):
        x = str(x).split("\nSans rendez-vous")[0]
        x = str(x).split("\nProvenance")[0]
        return x
