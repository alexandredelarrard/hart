import pandas as pd 
import numpy as np
import os 
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

        self.webpage_url = "https://www.sothebys.com/"
  
    @timing
    def clean_auctions(self, df_auctions):
        df_auctions = df_auctions.drop_duplicates(self.name.url_auction)
        df_auctions[self.name.id_auction] = df_auctions[self.name.url_auction].str.replace(self.webpage_url, "").apply(lambda x: "-".join(str(x).split("/")[-2:]).replace(".html", ""))
        df_auctions[self.name.type_sale] = df_auctions[self.name.type_sale].str.replace("CATEGORY:\n", "").str.lower()
        return df_auctions
    
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
        df = df.drop_duplicates(self.name.url_full_detail).reset_index(drop=True)

        # missing auction title 
        df[self.name.auction_title] = df[self.name.item_file].apply(lambda x: " ".join(x.split("-")[:-1]))
        df = df.rename(columns={self.name.brut_result : self.name.brut_estimate})
        df[self.name.brut_result] = np.nan

        # add hour cleaning info 
        df = self.extract_hour_infos(df)

        # clean url picture : 
        df[self.name.url_picture] = np.where(df[self.name.url_picture].apply(lambda x: "data:image/svg+xml;base64," in x),
                                             np.nan, 
                                             df[self.name.url_picture])
        
        # add ID AUCTION 
        df[self.name.id_auction] = df[self.name.date].str[:4] + "-" + df[self.name.item_file]

        return df

    @timing
    def explode_df_per_picture(self, df):
        df["CONDITION"] = np.where(df["CONDITION"] == "", np.nan, df["CONDITION"])
        df[self.name.detailed_description] = np.where(df[self.name.detailed_description] == "", np.nan, df[self.name.detailed_description])
        df[self.name.detailed_description] = np.where(df["CONDITION"].notnull()&df[self.name.detailed_description].notnull(),
                                                df[self.name.detailed_description]+  ". Other description : " +  df["CONDITION"],
                                            np.where(df["CONDITION"].notnull()&df[self.name.detailed_description].isnull(),
                                                df["CONDITION"],
                                                df[self.name.detailed_description]))
        del df["CONDITION"]
        return df
    