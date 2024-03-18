import pandas as pd 
from tqdm import tqdm
import numpy as np
import re
import os 
from glob import glob 
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR')

from src.context import Context
from src.datacrawl.transformers.TextCleaner import TextCleaner
from src.utils.timing import timing

from src.utils.utils_crawler import read_crawled_csvs

from omegaconf import DictConfig


class StepTextCleanChristies(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)

        self.seller = "christies"
        self.info_path = self._config.crawling[self.seller].save_data_path
        self.auctions_data_path = self._config.crawling[self.seller].save_data_path_auctions
        self.webpage_url = self._config.crawling[self.seller].webpage_url
        
        try:
            self.sql_table_name = self._config.embedding[self.seller].origine_table_name
        except Exception as e:
            self._log.error(f"SELLER not found in config embedding_history : {self.seller} \ {e}")
        
    @timing
    def run(self):
        
        # CLEAN AUCTIONS
        df_auctions = read_crawled_csvs(path=self.auctions_data_path)
        df_auctions = self.clean_auctions(df_auctions)

        # # CLEAN ITEMS
        df = read_crawled_csvs(path= self.info_path)
        df = self.clean_items_per_auction(df)

        # CLEAN DETAILED ITEM DATA
        # TODO:

        #MERGE ITEM & AUCTIONS
        df = self.concatenate_infos(df, df_auctions)

        # MERGE DETAILED ITEM DATA 
        # TODO:

        # SAVE ITEMS ENRICHED
        self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name,
                            if_exists="replace")
        
        return df

    @timing
    def clean_auctions(self, df_auctions):

        # URL auction clean
        df_auctions["URL_AUCTION"] = list(map(lambda x: x[:-1] if x[-1] == "/" else x,  df_auctions["URL_AUCTION"].tolist()))
        df_auctions["URL_AUCTION"] = list(map(lambda x: os.path.basename(x),  df_auctions["URL_AUCTION"].tolist()))

        # LOCALISATION
        df_auctions["LOCALISATION"] = list(map(lambda x: str(x).replace("EVENT LOCATION\n", ""),  df_auctions["LOCALISATION"].tolist()))
        df_auctions["DATE"] = pd.to_datetime(df_auctions["FILE"], format = "month=%m&year=%Y.csv")
    
        return df_auctions

    @timing
    def clean_items_per_auction(self, df):

        df["FILE"] = df["FILE"].str.replace(".csv","")
        df["LOT"] = df["LOT"].str.replace("LOT ","")
        df["RESULT"] =  self.get_estimate(df["RESULT"], min_max="min")
        df["RESULT_CURRENCY"] = self.get_currency_from_text(df["RESULT"])
        df["ESTIMATE_CURRENCY"] = self.get_currency_from_text(df["SALE"])

        df["CURRENCY"] = np.where(df["ESTIMATE_CURRENCY"].isin(["This lot has been withdrawn from auction", 
                                                                "Estimate on request", 
                                                                "Estimate unknown"]), np.nan,
                                  df["ESTIMATE_CURRENCY"]) # ~2000 missing

        df["MIN_ESTIMATION"] = self.get_estimate(df["SALE"], min_max="min")
        df["MAX_ESTIMATION"] = self.get_estimate(df["SALE"], min_max="max")
        df["FINAL_RESULT"] = self.get_estimate(df["RESULT"], min_max="min")

        for col in ["FINAL_RESULT", "MIN_ESTIMATION", "MAX_ESTIMATION"]:
            df[col] = np.where(df[col].isin(["This lot has been withdrawn from auction", 
                                            "Estimate on request", 
                                            "Estimate unknown"]), 
                                np.nan, df[col])
            df[col] = df[col].astype(float)
        
        df["FINAL_RESULT"] = np.where(df["FINAL_RESULT"].isnull(), 
                                      df[["MIN_ESTIMATION", "MAX_ESTIMATION"]].mean(axis=1), 
                                      df["FINAL_RESULT"])

        df = df.loc[df["FINAL_RESULT"].notnull()].reset_index(drop=True)
    
        return df 
    
    @timing
    def extract_infos(self, df):

        # date, place, maison
        sale = self.get_splitted_infos(df["INFOS"], index=df.index, sep="\n") 
        df["TITLE"] = sale[1]
        df["DESCRIPTION"] = sale[2]

        for col in ["TITLE", "DESCRIPTION"]:
            df[col] = np.where(df[col].isin(["1 ^,,^^,,^", "Estimate", "Sans titre", "Untitled",
                                            "2 ^,,^^,,^", "3 ^,,^^,,^", "1 ^,,^", "6 ^,,^", "4 ^,,^",
                                            "5 ^,,^"]), np.nan, df[col])

        return df
    
    def concatenate_infos(self, df, df_auctions):
        return df.merge(df_auctions, left_on='FILE', right_on="URL_AUCTION", suffixes=("", "_AUCTION"))