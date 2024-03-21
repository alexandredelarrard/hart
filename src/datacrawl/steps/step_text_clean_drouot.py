import pandas as pd 
import numpy as np
import locale
import re
locale.setlocale(locale.LC_ALL, 'fr_FR')

from src.datacrawl.transformers.TextCleaner import TextCleaner
from src.context import Context
from src.utils.timing import timing

from src.utils.utils_crawler import (read_crawled_csvs,
                                     encode_file_name)

from omegaconf import DictConfig


class StepTextCleanDrouot(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 seller : str = "drouot"):

        super().__init__(context=context, config=config)

        self.seller = seller
        self.infos_data_path = self._config.crawling[self.seller].save_data_path

        try:
            self.sql_table_name = self._config.cleaning[seller].origine_table_name
        except Exception as e:
            raise Exception(f"SELLER not found in config embedding_history : {self.seller} - {e}")
        
    @timing
    def run(self):

        df = read_crawled_csvs(path= self.infos_data_path)
        df = self.extract_hour_infos(df)
        df = self.clean_items_per_auction(df)
        df = self.extract_estimates(df)
        df = self.extract_currency(df)
        df = self.clean_estimations(df, ["Résultat : Non Communiqué ", 
                                        "Résultat : Non Communiqué", 
                                        'Estimation : Manquante'])
        df = self.remove_missing_values(df)
        df = self.remove_features(df)

        self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name,
                            if_exists="replace")
        
        return df

    
    @timing
    def clean_items_per_auction(self, df):
        
        df["IS_ONLINE"] = 1*(df["TYPE"] == "Online")
        df["DESCRIPTION"] = df["INFOS"]

        liste_pictures_missing = df["PICTURE_ID"].value_counts().loc[
            df["PICTURE_ID"].value_counts() > limite].index
        self._log.info(f"SET PICTURES ID TO MISSING FOR {len(liste_pictures_missing)} \
                       picts having more than {limite} picts")
        
        df["PICTURE_ID"] = np.where(df["PICTURE_ID"].isin(list(liste_pictures_missing)), 
                                    np.nan, df["PICTURE_ID"])
        df["ID"] = df["URL_FULL_DETAILS"].apply(lambda x : encode_file_name(str(x)))
        df["ORIGIN"] = self.seller

        return df
    
    @timing
    def extract_currency(self, df):

        df["CURRENCY_RESULTS"] = self.get_currency_from_text(df["BRUT_RESULT"])
        df["CURRENCY_ESIMATES"] = self.get_currency_from_text(df["BRUT_ESTIMATE"])
        df["CURRENCY"] = np.where(~df["CURRENCY_ESIMATES"].isin(["Estimation : Manquante"]), 
                                  df["CURRENCY_ESIMATES"],
                                  df["CURRENCY_RESULTS"])
        return df

    @timing
    def extract_estimates(self, df):

        # extract selling price and estimation
        df_results = self.get_splitted_infos(df["ESTIMATION"], index=df.index, sep="/")
        df["BRUT_RESULT"], df["BRUT_ESTIMATE"] = df_results[0], df_results[1]

        df["FINAL_RESULT"] = self.get_estimate(df["BRUT_RESULT"], min_max="min")
        df["MIN_ESTIMATION"] = self.get_estimate(df["BRUT_ESTIMATE"], min_max="min")
        df["MAX_ESTIMATION"] = self.get_estimate(df["BRUT_ESTIMATE"], min_max="max")
        df["MAX_ESTIMATION"] = np.where(df["MAX_ESTIMATION"].apply(lambda x: str(x).isdigit()), 
                                        df["MAX_ESTIMATION"], 
                                        df["MIN_ESTIMATION"])
        return df
    

    @timing
    def extract_hour_infos(self, df):

        # date, place, maison
        df["DATE"] = df["DATE"].apply(lambda x : re.sub(r'\(.*?\)', "", str(x)).strip())
        df["DATE"] = pd.to_datetime(df["DATE"], format="%A %d %B %Y - %H:%M")
        df["HOUR"] = df["DATE"].dt.hour
        df["DATE"] = df["DATE"].dt.round("D")
        df["DATE"] = df["DATE"].dt.strftime("%Y-%m-%d")

        return df
    
    @timing
    def remove_features(self, df, limite=50):
        df = df.drop(["INFOS", "TYPE", "RESULTAT", "ESTIMATION", "BRUT_RESULT", 
                      "BRUT_ESTIMATE",
                      'CURRENCY_RESULTS', 'CURRENCY_ESIMATES'], axis=1)
        return df
    