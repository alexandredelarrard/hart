import pandas as pd 
import locale
import os 
import numpy as np

from src.context import Context
from src.dataclean.transformers.TextCleaner import TextCleaner
from src.utils.timing import timing
from src.constants.variables import date_format

from omegaconf import DictConfig

map_month = {"JAN": "JANVIER", "FÉV": "FÉVRIER", "MAR": "MARS", "AVR": "AVRIL", 
             "MAI": "MAI", "JUIN": "JUIN", "JUIL": "JUILLET", "AOÛ": "AOÛT", 
             "SEP": "SEPTEMBRE", "OCT": "OCTOBRE", "NOV": "NOVEMBRE", 
             "DÉC": "DÉCEMBRE"}

class CleanMillon(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)
        locale.setlocale(locale.LC_ALL, 'fr_FR')
        
   
    @timing
    def clean_auctions(self, df_auctions):
 
        df_auctions = df_auctions.loc[df_auctions[self.name.url_auction].notnull()]
        df_auctions[self.name.url_auction] = df_auctions[self.name.url_auction].apply(lambda x :x.replace("/resultat", ""))
        df_auctions[self.name.id_auction] = df_auctions[self.name.url_auction].apply(lambda x : os.path.basename(x))

        # DATE
        df_auctions[self.name.hour] = pd.to_datetime(df_auctions[self.name.hour].apply(lambda x: x.split("-")[0].strip().replace("00H00", "12H00").replace("02H00", "14H00")), format="%HH%M")
        df_auctions[self.name.date] = df_auctions[self.name.date].apply(lambda x: " ".join(x.split("-")[0].strip().split(" ")[1:]))
        len_date = df_auctions[self.name.date].apply(lambda x: len(x.split(" ")))
        df_auctions[self.name.date] = np.where(len_date == 2, df_auctions[self.name.date].astype(str) + " 2024", df_auctions[self.name.date])
        fragmented_date = df_auctions[self.name.date].apply(lambda x: x.split(" "))
        df_auctions[self.name.date] = fragmented_date.apply(lambda x: " ".join([x[0], map_month[x[1]], x[2]]))
        df_auctions[self.name.date] = pd.to_datetime(df_auctions[self.name.date], format="%d %B %Y").dt.strftime(date_format)

        #LOCALISATION
        df_auctions[self.name.type_sale] = np.where(df_auctions[self.name.localisation].isin(["ONLINE", 'WWW.DROUOTONLINE.COM']), 1, 0)
        df_auctions[self.name.localisation] = np.where(df_auctions[self.name.localisation].isin(['NICE', 'NICE, 51 RUE BEAUMONT, 06300 NICE',
                                                                                                 '51 RUE BEAUMONT, 06300 NICE',
                                                                                                 'NICE, 3 PLACE FRANKLIN', '3 PLACE FRANKLIN, 06000 - NICE']), "nice",
                                            np.where(df_auctions[self.name.localisation].isin(['NANTES']), "nantes",
                                            np.where(df_auctions[self.name.localisation].isin(['NEUILLY-SUR-MARNE', 'NEULLY-SUR-MARNE', 
                                                                                                '116 BOULEVARD LOUIS-ARMAND, NEUILLY-SUR-MARNE 93330']), "neuilly-sur-marne",   
                                            np.where(df_auctions[self.name.localisation].isin(['LYON VENTE']), "lyon",
                                            np.where(df_auctions[self.name.localisation].isin(['LES FRANCISCAINES - DEAUVILLE',
                                                                                               'CENTRE INTERNATIONAL DEAUVILLE CID | PALAIS DES CONGRÈS DE DEAUVILLE_ SALON ART SHOPPING']), "deauville",
                                            np.where(df_auctions[self.name.localisation].isin(['LA CROIX-VALMER']), "croix-valmer", "paris"))))))

        return df_auctions

    @timing
    def clean_items_per_auction(self, df):

        df = df.loc[df[self.name.url_full_detail].notnull()]

        # CLEAN RESULT
        df[self.name.brut_result] = df[self.name.item_result].apply(lambda x: str(x).split("\n")[-1].replace("€", "EUR"))
        df[self.name.lot] = df[self.name.lot].str.replace("LOT ","")
        df[self.name.url_auction] = df[self.name.url_auction].apply(lambda x : str(x).split("/page")[0].replace("/resultat", ""))
        df[self.name.id_auction] = df[self.name.url_auction].apply(lambda x : os.path.basename(str(x).replace("/resultat", "")))
        
        assert df[self.name.url_auction].nunique() == df[self.name.id_auction].nunique()

        # date, place, maison
        df[self.name.item_infos] = np.where(df[self.name.item_infos]== "nan", np.nan, df[self.name.item_infos])
        df[self.name.item_description] = df[self.name.item_infos]

        return df
        
    @timing
    def clean_details_per_item(self, df):

        # clean estimate coming from detail 
        df = df.drop([self.name.brut_estimate, self.name.min_estimate, self.name.max_estimate], axis=1)
        df = df.rename(columns={self.name.brut_estimate + "_DETAIL": self.name.brut_estimate,
                                self.name.min_estimate +"_DETAIL": self.name.min_estimate,
                                self.name.max_estimate + "_DETAIL": self.name.max_estimate})
        df = self.extract_estimates(df) # text cleaner

        df[self.name.url_picture] = np.where(df[self.name.url_picture].isnull(),
                                             df[self.name.url_picture].apply(lambda x: [x]),
                                             df[self.name.url_picture])
        
        df = df.explode(self.name.url_picture) # from 3.3 to 10.8M rows
        df = df.drop([self.name.date, self.name.auction_title], axis=1)
        

        return df 
