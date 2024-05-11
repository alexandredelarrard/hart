import pandas as pd 
import numpy as np
import locale
import re


from src.dataclean.transformers.TextCleaner import TextCleaner
from src.context import Context
from src.utils.timing import timing
from src.constants.variables import localisation, currencies, date_format

from src.utils.utils_crawler import (read_crawled_csvs,
                                     read_crawled_pickles)

from omegaconf import DictConfig


class StepTextCleanSothebys(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 seller : str = "sothebys"):

        super().__init__(context=context, config=config)
        locale.setlocale(locale.LC_ALL, 'en')

        self.seller = seller
        self.infos_data_path = self._config.crawling[self.seller].save_data_path
        self.details_data_path = self._config.crawling[self.seller].save_data_path_details
        self.auctions_data_path = self._config.crawling[self.seller].save_data_path_auctions
        
        self.details_col_names = self.name.dict_rename_detail()
        self.items_col_names= self.name.dict_rename_items()
        self.auctions_col_names= self.name.dict_rename_auctions()

        self.sql_table_name = self.get_sql_db_name(self.seller)
        
    @timing
    def run(self):

        df = read_crawled_csvs(path= self.infos_data_path)
        df = self.renaming_dataframe(df, mapping_names=self.items_col_names)
        df = self.extract_hour_infos(df)
        df = self.clean_id_picture(df)
        df = self.clean_items_per_auction(df)
        df = self.extract_estimates(df)
        df = self.extract_currency(df)
        df = self.add_complementary_variables(df, self.seller)
        df = self.clean_estimations(df, [])
        df = self.remove_missing_values(df)
        df = self.remove_features(df, [self.name.item_infos, 
                                        self.name.brut_result])

        #merge with items 
        df_detailed = read_crawled_pickles(path=self.details_data_path)
        df_detailed = self.renaming_dataframe(df_detailed, mapping_names=self.details_col_names)
        df_detailed = self.complement_with_condition(df_detailed)
        df_detailed = self.clean_detail_infos(df_detailed)
        df_detailed = self.remove_features(df_detailed, ["NOTE_CATALOGUE", 
                                                         "ARTIST"])
        

        # MERGE DETAILED ITEM DATA 
        df = self.concatenate_detail(df, df_detailed)

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
        df[self.name.date] = df[self.name.date].dt.strftime(date_format)

        return df
    
    @timing
    def clean_items_per_auction(self, df):
        
        df[self.name.item_description] = df[self.name.item_infos]
        df[self.name.item_file] = df[self.name.item_file].str.replace(".csv","")
        df[self.name.lot] = df[self.name.item_description].apply(lambda x: x.split(".")[0].replace("No reserve\n", ""))

        #error of url full detail need to be corrected 
        df[self.name.url_full_detail] = df[[self.name.url_full_detail, self.name.lot]].apply(lambda x : 
                    re.sub("lot.(\\d+)+", f"lot.{x[self.name.lot]}", str(x[self.name.url_full_detail])), axis=1)

        # because sothebys crawling creates duplicates 
        df = df.drop_duplicates([self.name.url_full_detail]).reset_index(drop=True)

        # missing auction title 
        df[self.name.auction_title] = df[self.name.item_file].apply(lambda x: " ".join(x.split("-")[:-1]))

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
        df[self.name.currency] = np.where(df[self.name.currency].isin([
                                                "No reserve", 
                                                "Estimate Upon Request"]), np.nan,
                                  df[self.name.currency]) # ~2000 missing
        return df
    
    @timing
    def complement_with_condition(self, df_detailed):
        df_detailed[self.name.detailed_description] = (df_detailed[self.name.detailed_description].fillna("") + 
                                                       ". " + 
                                                       df_detailed["CONDITION"].fillna(""))
        return df_detailed
    