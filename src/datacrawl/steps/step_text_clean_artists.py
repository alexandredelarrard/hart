import re
import pandas as pd 
import numpy as np

from src.context import Context
from src.datacrawl.transformers.TextCleaner import TextCleaner
from src.utils.timing import timing
from nltk.tokenize import word_tokenize
from src.utils.utils_crawler import (read_crawled_pickles,
                                     read_crawled_csvs)

from omegaconf import DictConfig


class StepTextCleanArtists(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)

        self.artist_data_path = self._config.side_crawling.artist_db.save_data_path
        self.sql_table_name = self._config.cleaning.artists.origine_table_name
        
    @timing
    def run(self):

        # CLEAN DETAILED ITEM DATA
        df = read_crawled_csvs(path=self.artist_data_path)
        df = self.get_artist_dates(df)
        df = self.get_name_from_text(df)
        df = self.remove_features(df, ["FILE"])
    
        # SAVE ITEMS ENRICHED
        self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name,
                            if_exists="replace")
        
        return df
    
    def get_artist_dates(self, df):
        def findall(x):
            try:
                return re.search("\\((.*?)\\)", x).group(1)
            except Exception:
                return ""
        
        # extract years of born and death 
        dates = df["ARTIST_NAME"].apply(lambda x: findall(x).split("-"))
        df_dates = pd.DataFrame(dates.tolist())
        df[self._artist.artist_year_born] = df_dates[0]
        df[self._artist.artist_year_death] = df_dates[1]

        # clean values 
        for col in [self._artist.artist_year_born, self._artist.artist_year_death]:
            df[col] = np.where(df[col].notnull(),
                               df[col].apply(lambda x: self.clean_date_string(x)),
                               np.nan)
            df[col] = df[col].fillna("-1").astype(int).replace(-1, np.nan)
        
        return df

    def get_name_from_text(self, df):
        def extract_upper(liste):
            try:
                return " ".join([a for a in liste if a.isupper()])
            except Exception:
                return ""
        
        df["ARTIST_NAME"] = df["ARTIST_NAME"].apply(lambda x: re.sub("\\((.*?)\\)", "", x))
        df[self._artist.artist_family_name] = df["ARTIST_NAME"].apply(lambda x: extract_upper(word_tokenize(x)))
        df[self._artist.artist_surname] = df[["ARTIST_NAME", self._artist.artist_family_name]].apply(lambda x: x[0].replace(x[1], "").strip(), axis=1)
        
        for col in [self._artist.artist_family_name, self._artist.artist_surname]:
            df[col] = np.where(df[col] == "", np.nan, df[col])
        
        return df

    def clean_date_string(self, x):

        x = str(x)
        x = x.replace("XXI", "2015")
        x = x.replace("XX", "1915")
        x = x.replace("XIX", "1815")
        x = x.replace("XVIII", "1715")
        x = x.replace("XVII", "1615")
        x = x.replace("XVI", "1515")
        x = x.replace("XV", "1415")
        x = x.replace("XI", "1015")

        try:
            return re.findall("(\\d+)", x)[-1]
        except Exception:
            return np.nan
