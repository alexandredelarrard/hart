import pandas as pd 
import numpy as np
import os 

from src.context import Context
from src.dataclean.transformers.TextCleaner import TextCleaner
from src.utils.timing import timing
from src.constants.variables import date_format

from src.utils.utils_crawler import (read_crawled_csvs,
                                     read_pickle,
                                     read_crawled_pickles)

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
        self.details_data_path = self._config.crawling[self.seller].save_data_path_details

        self.details_col_names = self.name.dict_rename_detail()
        self.items_col_names= self.name.dict_rename_items()
        self.auctions_col_names= self.name.dict_rename_auctions()
        
        self.sql_table_name = self.get_sql_db_name(self.seller)
        
    @timing
    def run(self):
        
        # CLEAN AUCTIONS
        df_auctions = read_crawled_csvs(path=self.auctions_data_path)
        df_auctions = self.renaming_dataframe(df_auctions, mapping_names=self.auctions_col_names)
        mapping_corr_urls_auction = read_pickle(path=self.correction_urls_auction)
        df_auctions = self.clean_auctions(df_auctions, mapping_corr_urls_auction)

        # # CLEAN ITEMS
        df = read_crawled_csvs(path= self.info_path)
        df = self.renaming_dataframe(df, mapping_names=self.items_col_names)
        df = self.clean_items_per_auction(df)
        df = self.clean_id_picture(df) # 33% no pict
        df = self.extract_estimates(df)
        df = self.extract_currency(df)
        df = self.add_complementary_variables(df, self.seller)
        df = self.clean_estimations(df, ["This lot has been withdrawn from auction", 
                                        "Estimate on request", 
                                        "Estimate unknown",
                                        "Price realised", 
                                        "Price Realised"])
        df = self.remove_missing_values(df)
        df = self.extract_infos(df)

        # CLEAN DETAILED ITEM DATA
        df_detailed = read_crawled_pickles(path=self.details_data_path)
        df_detailed = self.renaming_dataframe(df_detailed, mapping_names=self.details_col_names)
        df_detailed = self.clean_detail_infos(df_detailed)

        # MERGE DETAILED ITEM DATA 
        df = self.concatenate_detail(df, df_detailed)

        #MERGE ITEM & AUCTIONS
        df = self.concatenate_auctions(df, df_auctions)
        df = self.remove_features(df, [self.name.item_infos, 
                                       self.name.brut_estimate, 
                                        self.name.brut_result])
    
        # SAVE ITEMS ENRICHED
        self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name,
                            if_exists="replace")
        
        return df


    @timing
    def clean_auctions(self, df_auctions, mapping_corr_urls_auction):

        # URL auction clean
        df_auctions["CORRECTED_URL"] = df_auctions[self.name.url_auction].map(mapping_corr_urls_auction)
        corrected_id_auction = df_auctions["CORRECTED_URL"].apply(lambda x : str(x).split("/")[-1])
        
        df_auctions[self.name.url_auction] = list(map(lambda x: x[:-1] if x[-1] == "/" else x,  df_auctions[self.name.url_auction].tolist()))
        df_auctions[self.name.url_auction] = list(map(lambda x: os.path.basename(x),  df_auctions[self.name.url_auction].tolist()))
        df_auctions[self.name.id_auction] = df_auctions[self.name.url_auction].apply(lambda x : str(x).split("-")[-1])
        df_auctions[self.name.id_auction] = np.where(corrected_id_auction == "nan", 
                                             df_auctions[self.name.id_auction], 
                                             corrected_id_auction)

        # LOCALISATION
        df_auctions[self.name.localisation] = list(map(lambda x: str(x).replace("EVENT LOCATION\n", ""),  df_auctions[self.name.localisation].tolist()))
        df_auctions[self.name.date] = pd.to_datetime(df_auctions[self.name.auction_file], format = "month=%m&year=%Y.csv")
        df_auctions[self.name.date] = df_auctions[self.name.date].dt.strftime(date_format)
    
        return df_auctions

    @timing
    def clean_items_per_auction(self, df):
        df[self.name.item_file] = df[self.name.item_file].str.replace(".csv","")
        df[self.name.lot] = df[self.name.lot].str.replace("LOT ","")
        df[self.name.id_auction] = df[self.name.item_file].apply(lambda x : str(x).split("&")[0].split("-")[-1])
        df[self.name.item_file] = df[self.name.item_file].apply(lambda x : str(x).split("&")[0])
        return df

    @timing
    def extract_estimates(self, df):
        df[self.name.min_estimate] = self.get_estimate(df[self.name.brut_estimate], min_max="min")
        df[self.name.max_estimate] = self.get_estimate(df[self.name.brut_estimate], min_max="max")
        df[self.name.item_result] = self.get_estimate(df[self.name.brut_result], min_max="min")
        return df 
    
    @timing
    def extract_currency(self, df):
        currency_brut_estimate = self.get_list_element_from_text(df[self.name.brut_estimate])
        df[self.name.currency] = np.where(currency_brut_estimate.isin(["This lot has been withdrawn from auction", 
                                                                "Estimate on request", 
                                                                "Estimate unknown"]), np.nan,
                                            currency_brut_estimate) # ~2000 missing
        return df
    
    @timing
    def extract_infos(self, df):

        # drop duplicates url full detail 
        df = df.drop_duplicates(self.name.url_full_detail).reset_index(drop=True)

        # date, place, maison
        sale = self.get_splitted_infos(df[self.name.item_infos], index=df.index, sep="\n") 
        df[self.name.item_title] = sale[1]
        df[self.name.item_description] = sale[2]

        for col in [self.name.item_title, self.name.item_description]:
            df[col] = np.where(df[col].str.lower().isin(["1 ^,,^^,,^", "estimate", "sans titre", "untitled",
                                            "2 ^,,^^,,^", "3 ^,,^^,,^", "1 ^,,^", "6 ^,,^", "4 ^,,^",
                                            "5 ^,,^"]), np.nan, df[col])
        
        return df
    
    @timing
    def concatenate_auctions(self, df, df_auctions):
        return df.merge(df_auctions, how="left", on=self.name.id_auction, 
                        validate="m:1", suffixes=("", "_AUCTION"))