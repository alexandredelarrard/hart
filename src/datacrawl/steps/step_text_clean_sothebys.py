import pandas as pd 
import numpy as np
import locale
import re
locale.setlocale(locale.LC_ALL, 'en')

from src.datacrawl.transformers.TextCleaner import TextCleaner
from src.context import Context
from src.utils.timing import timing
from src.constants.variables import localisation, currencies

from src.utils.utils_crawler import (read_crawled_csvs,
                                     encode_file_name)

from omegaconf import DictConfig


class StepTextCleanSothebys(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 seller : str = "sothebys"):

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
        df = self.clean_estimations(df, [])
        df = self.remove_missing_values(df)
        df = self.remove_features(df)

        self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name,
                            if_exists="replace")
        
        return df

    @timing
    def extract_hour_infos(self, df):

        # date, place, maison
        df["LOCALISATION"] = self.get_list_element_from_text(df["DATE"], liste=localisation)

        df["DATE"] = df["DATE"].apply(lambda x : str(x).split("•")[0].strip())
        df["DATE"] = pd.to_datetime(df["DATE"], format="%d %B %Y", exact=False)
        df["DATE"] = df["DATE"].dt.strftime("%Y-%m-%d")

        return df
    
    @timing
    def clean_items_per_auction(self, df, limite=100):
        
        df["DESCRIPTION"] = df["INFOS"]
        df["FILE"] = df["FILE"].str.replace(".csv","")
        df["LOT"] = df["DESCRIPTION"].apply(lambda x: x.split(".")[0])

        #error of url full detail need to be corrected 
        df["URL_FULL_DETAILS"] = df[["URL_FULL_DETAILS", "LOT"]].apply(lambda x : 
                    re.sub("lot.(\\d+)+", f"lot.{x["LOT"]}", str(x["URL_FULL_DETAILS"])), axis=1)

        liste_pictures_missing = df["PICTURE_ID"].value_counts().loc[
            df["PICTURE_ID"].value_counts() > limite].index
        self._log.info(f"SET PICTURES ID TO MISSING FOR {len(liste_pictures_missing)} \
                       picts having more than {limite} picts")
        
        df["PICTURE_ID"] = np.where(df["PICTURE_ID"].isin(list(liste_pictures_missing)), 
                                    np.nan, df["PICTURE_ID"])
        df["ID"] = df["URL_FULL_DETAILS"].apply(lambda x : encode_file_name(str(x)))
        df["ORIGIN"] = self.seller

        # because sothebys crawling creates duplicates 
        df = df.drop_duplicates(["URL_FULL_DETAILS"]).reset_index(drop=True)

        return df

    @timing
    def extract_estimates(self, df):
        df["MIN_ESTIMATION"] = self.get_estimate(df["RESULT"], min_max="min")
        df["MAX_ESTIMATION"] = self.get_estimate(df["RESULT"], min_max="max")
        df["FINAL_RESULT"] = np.nan
        return df 

    @timing
    def extract_currency(self, df):
        df["CURRENCY"] = self.get_list_element_from_text(df["RESULT"], liste=currencies)

        df["CURRENCY"] = np.where(df["CURRENCY"].isin(["No reserve", 
                                                "Estimate Upon Request"]), np.nan,
                                  df["CURRENCY"]) # ~2000 missing
        return df
    
    @timing
    def remove_features(self, df):
        df = df.drop(["INFOS", "RESULT"], axis=1)
        return df
