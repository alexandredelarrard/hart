import pandas as pd 
import numpy as np
import os 
import tqdm
import time
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR')

from src.context import Context
from src.datacrawl.transformers.TextCleaner import TextCleaner
from src.utils.timing import timing

from src.utils.utils_crawler import (read_crawled_csvs,
                                     encode_file_name,
                                     read_pickle)

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
        self.correction_urls_auction = self._config.crawling[self.seller].correction_urls_auction
        
        try:
            self.sql_table_name = self._config.cleaning[self.seller].origine_table_name
        except Exception as e:
            raise Exception(f"SELLER not found in config embedding_history : {self.seller} - {e}")
        
    @timing
    def run(self):
        
        # CLEAN AUCTIONS
        df_auctions = read_crawled_csvs(path=self.auctions_data_path)
        mapping_corr_urls_auction = read_pickle(path=self.correction_urls_auction)
        df_auctions = self.clean_auctions(df_auctions, mapping_corr_urls_auction)

        # # CLEAN ITEMS
        df = read_crawled_csvs(path= self.info_path)
        df = self.clean_items_per_auction(df)
        df = self.extract_estimates(df)
        df = self.extract_currency(df)
        df = self.clean_estimations(df, ["This lot has been withdrawn from auction", 
                                        "Estimate on request", 
                                        "Estimate unknown",
                                        "Price realised", 
                                        "Price Realised"])
        df = self.remove_missing_values(df)
        df = self.extract_infos(df)

        # CLEAN DETAILED ITEM DATA
        # TODO:

        #MERGE ITEM & AUCTIONS
        df = self.concatenate_infos(df, df_auctions)
        df = self.remove_features(df)

        # MERGE DETAILED ITEM DATA 
        # TODO:

        # SAVE ITEMS ENRICHED
        self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name,
                            if_exists="replace")
        
        return df


    @timing
    def clean_auctions(self, df_auctions, mapping_corr_urls_auction):

        # URL auction clean
        df_auctions["CORRECTED_URL"] = df_auctions["URL_AUCTION"].map(mapping_corr_urls_auction)
        df_auctions["CORRECTED_ID_AUCTION"] = df_auctions["CORRECTED_URL"].apply(lambda x : str(x).split("/")[-1])
        
        df_auctions["URL_AUCTION"] = list(map(lambda x: x[:-1] if x[-1] == "/" else x,  df_auctions["URL_AUCTION"].tolist()))
        df_auctions["URL_AUCTION"] = list(map(lambda x: os.path.basename(x),  df_auctions["URL_AUCTION"].tolist()))
        df_auctions["ID_AUCTION"] = df_auctions["URL_AUCTION"].apply(lambda x : str(x).split("-")[-1])
        df_auctions["ID_AUCTION"] = np.where(df_auctions["CORRECTED_ID_AUCTION"] == "nan", 
                                             df_auctions["ID_AUCTION"], 
                                             df_auctions["CORRECTED_ID_AUCTION"])
        df_auctions.rename(columns={"TITLE": "TITLE_AUCTION",
                                    "FILE" : "FILE_AUCTION"}, inplace=True)

        # LOCALISATION
        df_auctions["LOCALISATION"] = list(map(lambda x: str(x).replace("EVENT LOCATION\n", ""),  df_auctions["LOCALISATION"].tolist()))
        df_auctions["DATE"] = pd.to_datetime(df_auctions["FILE_AUCTION"], format = "month=%m&year=%Y.csv")
        df_auctions["DATE"] = df_auctions["DATE"].dt.strftime("%Y-%m-%d")
    
        return df_auctions

    @timing
    def clean_items_per_auction(self, df):

        df["FILE"] = df["FILE"].str.replace(".csv","")
        df["LOT"] = df["LOT"].str.replace("LOT ","")
        df["ID_AUCTION"] = df["FILE"].apply(lambda x : str(x).split("&")[0].split("-")[-1])
        df["FILE"] = df["FILE"].apply(lambda x : str(x).split("&")[0])

        df["PICTURE_ID"] = np.where(df["PICTURE_ID"].isin(["non_NoImag.jpg", "MISSING.jpg", 
                                                           "wine-lots.jpg", "allowedcountries_h.jpg"]), 
                                    np.nan, df["PICTURE_ID"])

        df["ID"] = df["URL_FULL_DETAILS"].apply(lambda x : encode_file_name(str(x)))
        df["ORIGIN"] = self.seller

        return df

    @timing
    def extract_estimates(self, df):
        df["RESULT"] =  self.get_estimate(df["RESULT"], min_max="min")
        df["MIN_ESTIMATION"] = self.get_estimate(df["SALE"], min_max="min")
        df["MAX_ESTIMATION"] = self.get_estimate(df["SALE"], min_max="max")
        df["FINAL_RESULT"] = self.get_estimate(df["RESULT"], min_max="min")
        return df 
    
    @timing
    def extract_currency(self, df):
        df["RESULT_CURRENCY"] = self.get_list_element_from_text(df["RESULT"])
        df["ESTIMATE_CURRENCY"] = self.get_list_element_from_text(df["SALE"])

        df["CURRENCY"] = np.where(df["ESTIMATE_CURRENCY"].isin(["This lot has been withdrawn from auction", 
                                                                "Estimate on request", 
                                                                "Estimate unknown"]), np.nan,
                                  df["ESTIMATE_CURRENCY"]) # ~2000 missing
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
        return df.merge(df_auctions, how="left", on="ID_AUCTION", 
                        validate="m:1", suffixes=("", "_AUCTION"))
    
    def remove_features(self, df):
        df = df.drop(["INFOS", "SALE", "RESULT", "CORRECTED_ID_AUCTION", 
                      'RESULT_CURRENCY', 'ESTIMATE_CURRENCY'], axis=1)
        return df