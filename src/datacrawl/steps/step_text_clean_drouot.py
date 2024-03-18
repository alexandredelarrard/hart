import pandas as pd 
import numpy as np
import re
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR')

from src.datacrawl.transformers.TextCleaner import TextCleaner
from src.context import Context
from src.utils.timing import timing

from src.constants.variables import currencies, category, materiau
from src.utils.utils_dataframe import remove_accents, remove_punctuation
from src.utils.utils_crawler import read_crawled_csvs

from omegaconf import DictConfig


class StepTextCleanDrouot(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 seller : str = "drouot"):

        super().__init__(context=context, config=config)

        self.seller = seller
        try:
            self.sql_table_name = self._config.embedding[seller].origine_table_name
        except Exception as e:
            self._log.error(f"SELLER not found in config embedding_history : {self.seller} \ {e}")
        
    @timing
    def run(self):

        files_path = self._config.crawling[self.seller].save_data_path

        df = read_crawled_csvs(path= files_path)
        df = self.extract_sale_infos(df)
        df = self.extract_infos(df)
        df = self.extract_estimates(df)
        df = self.extract_currency(df)
        df = self.extract_descriptions(df)

        self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name,
                            if_exists="replace")
        
        return df

    
    @timing
    def extract_infos(self, df):

        # INFOS 4 slides 
        df["INFOS"] = df["INFOS"].str.split("\n")
        df_infos =  pd.DataFrame(df["INFOS"].tolist(), index=df.index)
        df["LOT_ID"] = df_infos[0].str.replace("Lot n° ","").str.zfill(4)
        df["DESCRIPTION"] = df_infos[2]
        df["RESULTS"] = df_infos[3]

        # drop duplicated infos / estimates 
        df["PICTURE_ID"] = np.where(df["PICTURE_ID"].isnull(), 
                                    "MISSING" + "_" + df["LOT_ID"] + "_" + df["DATE"], 
                                    df["PICTURE_ID"])
        df = df.drop_duplicates("PICTURE_ID")

        # remove those without price 
        df = df.loc[df["RESULTS"].notnull()].reset_index(drop=True)

        return df
    
    @timing
    def extract_currency(self, df):

        df["CURRENCY_RESULTS"] = self.get_currency_from_text(df["BRUT_RESULT"])
        df["CURRENCY_ESIMATES"] = self.get_currency_from_text(df["BRUT_ESTIMATE"])
        
        df["CURRENCY"] = np.where(~df["CURRENCY_ESIMATES"].isin(["Estimation : Manquante"]), df["CURRENCY_ESIMATES"],
                                  df["CURRENCY_RESULTS"])

        return df

    @timing
    def extract_estimates(self, df):

        # extract selling price and estimation
        df_results = pd.DataFrame(df["RESULTS"].str.split('/').tolist(), index=df.index)
        df["BRUT_RESULT"], df["BRUT_ESTIMATE"] = df_results[0], df_results[1]

        index_estimation = df["BRUT_RESULT"].apply(lambda x: "Estimation" in x)
        df.loc[index_estimation, "BRUT_ESTIMATE"] = df.loc[index_estimation, "BRUT_RESULT"].tolist()
        df.loc[index_estimation, "BRUT_RESULT"] = "0"

        df["FINAL_RESULT"] = self.get_estimate(df["BRUT_RESULT"], min_max="min")
        
        df["BRUT_ESTIMATE"].fillna("Estimation : Manquante", inplace=True)
        df["MIN_ESTIMATION"] = self.get_estimate(df["BRUT_ESTIMATE"], min_max="min")
        df["MAX_ESTIMATION"] = self.get_estimate(df["BRUT_ESTIMATE"], min_max="max")
        df["MAX_ESTIMATION"] = np.where(df["MAX_ESTIMATION"].apply(lambda x: str(x).isdigit()), 
                                        df["MAX_ESTIMATION"], 
                                        df["MIN_ESTIMATION"])
        
        # mvs 
        for col in ["FINAL_RESULT", "MIN_ESTIMATION", "MAX_ESTIMATION"]:
            df[col] = np.where(df[col].isin(["Résultat : Non Communiqué ", 
                                            "Résultat : Non Communiqué", 
                                            'Estimation : Manquante']), 
                                np.nan, df[col])
            df[col] = df[col].astype(float)

        # keep only those with available estimates or result 
        df["FINAL_RESULT"] = np.where(df["FINAL_RESULT"].isnull(), 
                                      df[["MIN_ESTIMATION", "MAX_ESTIMATION"]].mean(axis=1), 
                                      df["FINAL_RESULT"])

        for col in ["MIN_ESTIMATION", "MAX_ESTIMATION"]:
            df[col] = np.where(df[col].isnull(), df["FINAL_RESULT"], df[col])

        df = df.loc[df["FINAL_RESULT"].notnull()].reset_index(drop=True)

        return df
    

    @timing
    def extract_sale_infos(self, df):

        # date, place, maison
        sale =  pd.DataFrame(df["SALE"].str.split('\n').tolist(), index=df.index)
        df["DATE"] = pd.to_datetime(sale[0], format="%A %d %b %Y - %H:%M")
        df["HOUR"] = df["DATE"].dt.hour
        df["DATE"] = df["DATE"].dt.round("D")
        df["PLACE"] = sale[1]
        df["HOUSE"] = sale[2]

        df["DATE"] = df["DATE"].dt.strftime("%Y-%m-%d")

        return df
    
    
    @timing
    def extract_descriptions(self, df):

        def get_element_in_list(x, liste):
            
            for a in liste:
                if a in x:
                    return a
            return x
        
        clean_category = [remove_punctuation(remove_accents(a)) for a in category]
        clean_materiau = [remove_punctuation(remove_accents(a)) for a in materiau]

        df["CLEAN_TEXT"] = df["DESCRIPTION"].apply(lambda x : remove_punctuation(remove_accents(x.lower())))
        df["CATEGORY"] = df["CLEAN_TEXT"].apply(lambda x: get_element_in_list(x, clean_category)) 
        df["MATERIAU"] = df["CLEAN_TEXT"].apply(lambda x: get_element_in_list(x, clean_materiau)) 

        # clean mvs
        df["ID"] = df["PICTURE_ID"].apply(lambda x : x.replace(".jpg", ""))
        df = df.drop(["INFOS", "SALE", "URL_PICTURE", "CLEAN_TEXT", "RESULTS"], axis=1)
        
        df["HOUSE"].fillna("MISSING_HOUSE", inplace=True)

        return df
