import pandas as pd 
import numpy as np
import locale
import re


from src.dataclean.transformers.TextCleaner import TextCleaner
from src.context import Context
from src.utils.timing import timing
from src.constants.variables import localisation, currencies, date_format

from omegaconf import DictConfig


class CleanSothebys(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)
        locale.setlocale(locale.LC_ALL, 'en')
  
  
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
        df[self.name.brut_estimate] = df[self.name.brut_result]

        # add hour cleaning info 
        df = self.extract_hour_infos(df)

        return df


    @timing
    def complement_with_condition(self, df_detailed):
        df_detailed[self.name.detailed_description] = (df_detailed[self.name.detailed_description].fillna("") + 
                                                       ". " + 
                                                       df_detailed["CONDITION"].fillna(""))
        return df_detailed
    
    def clean_detail_infos(self, df_detailed):
        df_detailed = self.complement_with_condition(df_detailed)
        df_detailed = self.clean_detail_infos(df_detailed)
        return df_detailed
    