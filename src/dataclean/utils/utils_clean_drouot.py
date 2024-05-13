import pandas as pd 
import numpy as np
import locale
import re
import os 

from src.dataclean.transformers.TextCleaner import TextCleaner
from src.context import Context
from src.utils.timing import timing
from src.constants.variables import date_format


from omegaconf import DictConfig


class CleanDrouot(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)
        locale.setlocale(locale.LC_ALL, 'fr_FR')
        self.root_path = self._config.crawling.root_path

    @timing
    def extract_hour_infos(self, df):
        df[self.name.date] = df[self.name.date].apply(lambda x : re.sub(r'\(.*?\)', "", str(x)).strip())
        df[self.name.date] = pd.to_datetime(df[self.name.date], format="%A %d %B %Y - %H:%M")
        df[self.name.hour] = df[self.name.date].dt.hour
        df[self.name.date] = df[self.name.date].dt.round("D")
        df[self.name.date] = df[self.name.date].dt.strftime(date_format)
        return df
    
    @timing
    def handle_type_of_sale(self, df):
        occurence = df[self.name.type_sale].unique()
        if len(occurence) == 2:
            df[self.name.type_sale] = 1*(df[self.name.type_sale] == "Online")
        else:
            raise Exception(f"DROUOT DATAPREP for {self.name.type_sale} expects 2 single occurence, {occurence} found")
        return df
    
    @timing
    def clean_items_per_auction(self, df):
        df[self.name.item_description] = df[self.name.item_infos]

        # clean localisation
        df[self.name.localisation] = np.where(df[self.name.place].isin(["www.drouot.com", 'Drouot Live ONLY - - -', 'Vente Huis Clos -']), "Hotel Drouot - 75009 Paris",
                                     np.where(df[self.name.place].apply(lambda x: "www.setdart.com" in x), "Arago, 346 - 08009 Barcelone, Espagne",  
                                     np.where(df[self.name.place]=="'- , Luxembourg'", "XXX - 001 Luxembourg, Luxembourg",
                                     np.where(df[self.name.place]=='- , Suisse', "XXX - 001 Genève, Suisse",   
                                     np.where(df[self.name.place]=='- , Royaume-Uni', "XXX - 001 London, Royaume uni",     
                                            df[self.name.place])))))
        df[self.name.localisation] = df[self.name.localisation].apply(lambda x: x.split(" - ")[-1].split(",")[0].strip().split(" ")[-1])
        df[self.name.localisation] = np.where(df[self.name.localisation].isin(['-', '- ,']), np.nan, df[self.name.localisation].str.lower())

         # extract selling price and estimation
        df_results = self.get_splitted_infos(df[self.name.brut_estimate], index=df.index, sep="/")
        df[self.name.brut_result], df[self.name.brut_estimate] = df_results[0], df_results[1]

        #handle type of sale and hours 
        df = self.extract_hour_infos(df)
        df = self.handle_type_of_sale(df)

        return df

    @timing
    def clean_pictures_url(self, df_detailed):
        col_list_urls = self.name.pictures_list_url
        df_detailed[col_list_urls] = np.where(df_detailed[col_list_urls].notnull(),
                                            df_detailed[col_list_urls].apply(lambda x: [a for c in [re.findall("url\(\"(.+?)\"\)", str(a)).replace("size=small", "size=phare") for a in x] for a in c]),
                                                # [str(a).split("url(")[-1].split(")")[0].replace("\"", "").replace("size=small", "size=phare") for a in x]),
                                            np.nan)
        df_detailed[col_list_urls] = df_detailed[col_list_urls].apply(lambda x: np.nan if len(x)==0 else x)
        return df_detailed
    
    
    @timing
    def explode_df_per_picture(self, df):

        df[self.name.url_picture] = np.where((df[self.name.pictures_list_url].isnull()), 
                                            df[self.name.url_picture].apply(lambda x: [x]),
                                            df[self.name.pictures_list_url])
        
        df = df.explode(self.name.url_picture) # from 3.3 to 6.4M rows

        # rename picture_ids based on url path
        df[self.name.id_picture] = df[self.name.url_picture].swifter.apply(lambda x: os.path.basename(str(x)))
        df[self.name.id_picture] = np.where(df[self.name.id_picture] == "nan", np.nan, df[self.name.id_picture])
        
        # keep ID picture when picture is available for drouot ~2.3M
        picture_path = df[self.name.id_picture].apply(lambda x : f"{self.root_path}/{self.seller}/pictures/{x}.jpg")
        exists_pict = picture_path.swifter.apply(lambda x : os.path.isfile(x))
        df[self.name.id_picture] = np.where(exists_pict, df[self.name.id_picture], np.nan)
        
        return df
    
    @timing
    def clean_detail_infos(self, df_detailed):
        df_detailed = self.clean_detail_infos(df_detailed)
        df_detailed = self.clean_pictures_url(df_detailed)
        return df_detailed
    
    @timing
    def clean_id_picture(self, df):
        df = self.explode_df_per_picture(df)
        df = self.clean_id_picture(df)
        return df
        

    