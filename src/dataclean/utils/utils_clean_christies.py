import pandas as pd 
import numpy as np
import os 

from src.context import Context
from src.dataclean.transformers.TextCleaner import TextCleaner
from src.utils.timing import timing
from src.constants.variables import date_format

from src.utils.utils_crawler import read_pickle

from omegaconf import DictConfig


class CleanChristies(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)
        self.correction_urls_auction = self._config.crawling[self.seller].correction_urls_auction
   
    @timing
    def clean_auctions(self, df_auctions):

        mapping_corr_urls_auction = read_pickle(path=self.correction_urls_auction)

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
        
        # date, place, maison
        sale = self.get_splitted_infos(df[self.name.item_infos], index=df.index, sep="\n") 
        df[self.name.item_title] = sale[1]
        df[self.name.item_description] = sale[2]

        return df
