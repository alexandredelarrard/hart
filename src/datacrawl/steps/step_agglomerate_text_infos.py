from typing import Dict
import pandas as pd 
from typing import List

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.constants.variables import list_sellers
from src.datacrawl.transformers.TextCleaner import TextCleaner

from omegaconf import DictConfig


class StepAgglomerateTextInfos(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)

        self.sql_table_name = self._config.cleaning.full_data_auction_houses
        self.table_names = {}
        for seller in list_sellers:
            self.table_names[seller] = self.get_sql_db_name(seller)


    @timing
    def run(self):

        df = self.concatenate_sellers()
        df = self.keep_relevant_features(df)
        df = self.homogenize_currencies(df)
        df = self.homogenize_location(df)
        df = self.homogenize_title(df)
        df = self.homogenize_description(df)

        self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name,
                            if_exists="replace")


    @timing
    def concatenate_sellers(self):
        final_df = pd.DataFrame()
        for seller in list_sellers: 
            df = pd.read_sql(self.table_names[seller], con=self._context.db_con)
            final_df = pd.concat([final_df, df], axis=0)
        return final_df

    @timing
    def keep_relevant_features(self, final_df):
        return final_df[[self.name.id_item,
                             self.name.lot, 
                             self.name.auction_date,
                             self.name.auction_hour,
                             self.name.item_title,
                             self.name.item_description,
                             self.name.min_estimate,
                             self.name.max_estimate,
                             self.name.item_result,
                             self.name.is_item_result,
                             self.name.currency,
                             self.name.id_picture,
                             self.name.localisation,
                             self.name.seller,
                             self.name.type_sale]]

    @timing
    def homogenize_currencies(self, df):
        return df 

    @timing
    def homogenize_location(self, df):
        return df 

    @timing
    def homogenize_title(self, df):
        return df 

    @timing
    def homogenize_description(self, df):
        return df 
