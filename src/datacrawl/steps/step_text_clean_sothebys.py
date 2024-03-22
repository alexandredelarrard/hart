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
        self.items_col_names= self.name.dict_rename_items()

        try:
            self.sql_table_name = self._config.cleaning[seller].origine_table_name
        except Exception as e:
            raise Exception(f"SELLER not found in config embedding_history : {self.seller} - {e}")
        
    @timing
    def run(self):

        df = read_crawled_csvs(path= self.infos_data_path)
        df = self.renaming_dataframe(df, mapping_names=self.items_col_names)
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
        df[self.name.localisation] = self.get_list_element_from_text(df[self.name.date], liste=localisation)

        df[self.name.date] = df[self.name.date].apply(lambda x : str(x).split("•")[0].strip())
        df[self.name.date] = pd.to_datetime(df[self.name.date], format="%d %B %Y", exact=False)
        df[self.name.date] = df[self.name.date].dt.strftime("%Y-%m-%d")

        return df
    
    @timing
    def clean_items_per_auction(self, df, limite=100):
        
        df[self.name.item_description] = df[self.name.item_infos]
        df[self.name.item_file] = df[self.name.item_file].str.replace(".csv","")
        df[self.name.lot] = df[self.name.item_description].apply(lambda x: x.split(".")[0])

        #error of url full detail need to be corrected 
        df[self.name.url_full_detail] = df[[self.name.url_full_detail, self.name.lot]].apply(lambda x : 
                    re.sub("lot.(\\d+)+", f"lot.{x[self.name.lot]}", str(x[self.name.url_full_detail])), axis=1)

        liste_pictures_missing = df[self.name.id_picture].value_counts().loc[
            df[self.name.id_picture].value_counts() > limite].index
        self._log.info(f"SET PICTURES ID TO MISSING FOR {len(liste_pictures_missing)} \
                       picts having more than {limite} picts")
        
        df[self.name.id_picture] = np.where(df[self.name.id_picture].isin(list(liste_pictures_missing)), 
                                    np.nan, df[self.name.id_picture])
        df[self.name.id_item] = df[self.name.url_full_detail].apply(lambda x : encode_file_name(str(x)))
        df[self.name.seller] = self.seller

        # because sothebys crawling creates duplicates 
        df = df.drop_duplicates([self.name.url_full_detail]).reset_index(drop=True)

        return df

    @timing
    def extract_estimates(self, df):
        df[self.name.min_estimate] = self.get_estimate(df[self.name.brut_result], min_max="min")
        df[self.name.max_estimate] = self.get_estimate(df[self.name.brut_result], min_max="max")
        df[self.name.item_result] = np.nan
        return df 

    @timing
    def extract_currency(self, df):
        df[self.name.currency] = self.get_list_element_from_text(df[self.name.brut_result], liste=currencies)

        df[self.name.currency] = np.where(df[self.name.currency].isin(["No reserve", 
                                                "Estimate Upon Request"]), np.nan,
                                  df[self.name.currency]) # ~2000 missing
        return df
    
    @timing
    def remove_features(self, df):
        df = df.drop([self.name.item_infos, self.name.brut_result], axis=1)
        return df
