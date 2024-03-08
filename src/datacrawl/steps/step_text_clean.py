import pandas as pd 
from tqdm import tqdm
import numpy as np
import re
from glob import glob 
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR')

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from src.datacrawl.constants.variables import currencies

from omegaconf import DictConfig


class StepTextClean(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 seller : str = "drouot"):

        super().__init__(context=context, config=config)
        self.seller = seller
        
    @timing
    def run(self):
        df = self.read_crawled_csvs()
        df, df_infos = self.extract_infos(df)
        df = self.extract_estimates(df, df_infos)
        df = self.extract_currency(df)
        df = self.extract_sale_infos(df)

        self.write_sql_data(dataframe=df,
                            table_name="DROUOT_202401")

    @timing
    def read_crawled_csvs(self):

        # read all csvs
        files = glob(self._config.crawling[self.seller].save_data_path + "/*.csv")
        
        liste_dfs = []
        for file in tqdm(files): 
            df_file = pd.read_csv(file, sep=";")
            df_file["KEYWORD"] = file.split("\\")[1].split("_")[0]
            liste_dfs.append(df_file)

        df = pd.concat(liste_dfs, axis=0, ignore_index=True)
        self._log.info(f"RECORDINGS : {df.shape[0]}")

        return df
    

    def extract_infos(self, df):

        # INFOS 4 slides 
        df["INFOS"] = df["INFOS"].str.split("\n")
        df_infos =  pd.DataFrame(df["INFOS"].tolist())
        df["LOT_ID"] = df_infos[0].str.replace("Lot n° ","").str.zfill(4)
        df["DESCRIPTION"] = df_infos[2]
        df["RESULTS"] = df_infos[3]

        # remove those without price 
        df = df.loc[df["RESULTS"].notnull()]
        df_infos = df_infos.loc[df_infos[3].notnull()]

        return df, df_infos
    

    def extract_currency(self, df):

        df["CURRENCY_RESULTS"] = df["BRUT_RESULT"].apply(lambda x : re.findall(currencies, x)[0] if 
                                             len(re.findall(currencies, x)) > 0 else x)
        df["CURRENCY_ESIMATES"] = df["BRUT_ESTIMATE"].apply(lambda x : re.findall(currencies, x)[0] if 
                                             len(re.findall(currencies, x)) > 0 else x)
        
        df["CURRENCY"] = np.where(~df["CURRENCY_ESIMATES"].isin(["Estimation : Manquante"]), df["CURRENCY_ESIMATES"],
                                  df["CURRENCY_RESULTS"])

        return df


    def extract_estimates(self, df, df_infos):

        # extract selling price and estimation
        df_results = pd.DataFrame(df_infos[3].str.split('/').tolist(), index=df_infos.index)
        df["BRUT_RESULT"], df["BRUT_ESTIMATE"] = df_results[0], df_results[1]

        index_estimation = df["BRUT_RESULT"].apply(lambda x: "Estimation" in x)
        df.loc[index_estimation, "BRUT_ESTIMATE"] = df.loc[index_estimation, "BRUT_RESULT"].tolist()
        df.loc[index_estimation, "BRUT_RESULT"] = "0"

        df["RESULTS"] = df["BRUT_RESULT"].apply(lambda x : re.findall(r"\d+", x.replace(" ",""))[0] if len(re.findall(r"\d+", x)) >0 else x)
        df["BRUT_ESTIMATE"].fillna("Estimation : Manquante", inplace=True)
        df["MIN_ESTIMATION"] = df["BRUT_ESTIMATE"].apply(lambda x : re.findall(r"\d+", str(x).replace(" ",""))[0] 
                                                   if len(re.findall(r"\d+", x)) > 0 else x)
        df["MAX_ESTIMATION"] = df["BRUT_ESTIMATE"].apply(lambda x : re.findall(r"\d+", str(x).replace(" ",""))[1] 
                                                   if len(re.findall(r"\d+", str(x).replace(" ",""))) == 2 else x)

        return df
    
    def extract_sale_infos(self, df):

        # date, place, maison
        sale =  pd.DataFrame(df["SALE"].str.split('\n').tolist(), index=df.index)
        df["DATE"] = pd.to_datetime(sale[0], format="%A %d %b %Y - %H:%M")
        df["PLACE"] = sale[1]
        df["HOUSE"] = sale[2]

        return df
    
    def extract_descriptions(self, df):

        df["CLEAN_TEXT"] = df["DESCRIPTION"].apply(lambda x : x.lower().strip())
        df["CLEAN_TEXT"] = 

