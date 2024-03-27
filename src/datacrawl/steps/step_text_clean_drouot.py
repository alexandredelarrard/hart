import pandas as pd 
import numpy as np
import locale
import re


from src.datacrawl.transformers.TextCleaner import TextCleaner
from src.context import Context
from src.utils.timing import timing
from src.constants.variables import date_format

from src.utils.utils_crawler import (read_crawled_csvs,
                                    read_crawled_pickles)

from omegaconf import DictConfig


class StepTextCleanDrouot(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 seller : str = "drouot"):

        super().__init__(context=context, config=config)
        locale.setlocale(locale.LC_ALL, 'fr_FR')

        self.seller = seller
        self.infos_data_path = self._config.crawling[self.seller].save_data_path
        self.details_data_path = self._config.crawling[self.seller].save_data_path_details
        
        self.details_col_names = self.name.dict_rename_detail()
        self.items_col_names= self.name.dict_rename_items()

        self.sql_table_name = self.get_sql_db_name(self.seller)
        
    @timing
    def run(self):

        df = read_crawled_csvs(path= self.infos_data_path)
        df = self.renaming_dataframe(df, mapping_names=self.items_col_names)
        df = self.extract_hour_infos(df)
        df = self.handle_type_of_sale(df)
        df = self.clean_id_picture(df)
        df = self.clean_items_per_auction(df)
        df = self.extract_estimates(df)
        df = self.extract_currency(df)
        df = self.add_complementary_variables(df, self.seller)
        df = self.clean_estimations(df, ["Résultat : Non Communiqué ", 
                                        "Résultat : Non Communiqué", 
                                        'Estimation : Manquante'])
        df = self.remove_missing_values(df)
        df = self.extract_infos(df)
        df = self.remove_features(df, [self.name.item_infos, 
                                       self.name.brut_estimate, 
                                        self.name.brut_result])

        #merge with items 
        df_detailed = read_crawled_pickles(path=self.details_data_path)
        df_detailed = self.renaming_dataframe(df_detailed, mapping_names=self.details_col_names)
        df_detailed = self.clean_detail_infos(df_detailed)

        # MERGE DETAILED ITEM DATA 
        df = self.concatenate_detail(df, df_detailed)

        self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name,
                            if_exists="replace")
        
        return df
    
    @timing
    def extract_hour_infos(self, df):

        # date, place, maison
        df[self.name.date] = df[self.name.date].apply(lambda x : re.sub(r'\(.*?\)', "", str(x)).strip())
        df[self.name.date] = pd.to_datetime(df[self.name.date], format="%A %d %B %Y - %H:%M")
        df[self.name.hour] = df[self.name.date].dt.hour
        df[self.name.date] = df[self.name.date].dt.round("D")
        df[self.name.date] = df[self.name.date].dt.strftime(date_format)

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
    def extract_estimates(self, df):

        # extract selling price and estimation
        df_results = self.get_splitted_infos(df[self.name.brut_estimate], index=df.index, sep="/")
        df[self.name.brut_result], df[self.name.brut_estimate] = df_results[0], df_results[1]

        df[self.name.item_result] = self.get_estimate(df[self.name.brut_result], min_max="min")
        df[self.name.min_estimate] = self.get_estimate(df[self.name.brut_estimate], min_max="min")
        df[self.name.max_estimate] = self.get_estimate(df[self.name.brut_estimate], min_max="max")
        df[self.name.max_estimate] = np.where(df[self.name.max_estimate].apply(lambda x: str(x).isdigit()), 
                                        df[self.name.max_estimate], 
                                        df[self.name.min_estimate])
        return df

    @timing
    def extract_currency(self, df):

        currency_brut_results = self.get_list_element_from_text(df[self.name.brut_result])
        currency_brut_estimate = self.get_list_element_from_text(df[self.name.brut_estimate])
        df[self.name.currency] = np.where(~currency_brut_estimate.isin(["Estimation : Manquante"]), 
                                            currency_brut_estimate,
                                            currency_brut_results)
        return df

    @timing
    def extract_infos(self, df):

        # drop duplicates url full detail 
        df = df.drop_duplicates(self.name.url_full_detail).reset_index(drop=True)

        for col in [self.name.item_title, self.name.item_description]:
            df[col] = np.where(df[col].str.lower().isin(["--> ce lot se trouve au depot", "retrait",
                                                        "lot non venu", ".",
                                                        "aucune désignation", "withdrawn", "pas de lot",
                                                        "no lot", "retiré",
                                                        "pas venu", "40", "lot retiré", "20", "test", 
                                                        "300", "non venu", "--> ce lot se trouve au depôt",
                                                        "hors catalogue", '()']), np.nan, df[col])
        
        return df
    