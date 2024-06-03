from typing import Dict
import numpy as np
import pandas as pd 
from datetime import datetime
import swifter
import langid

from src.context import Context
from src.utils.timing import timing
from src.constants.variables import (liste_currency_paires, 
                                    fixed_eur_rate,
                                    date_format)

from src.dataclean.transformers.TextCleaner import TextCleaner
from src.utils.utils_dataframe import (remove_accents,
                                       flatten_dict)
from src.utils.utils_currencies import extract_currencies
from src.utils.dataset_retreival import DatasetRetreiver

from omegaconf import DictConfig


class StepAgglomerateTextInfos(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 mode: str = "history"):

        super().__init__(context=context, config=config)

        self.sql_table_name = self._config.cleaning.full_data_auction_houses
        self.sql_table_name_per_item = self.sql_table_name + "_per_item"
        self.country_mapping  = self._config.cleaning.mapping.country
        self.localisation_mapping = self._config.cleaning.mapping.localisation
        self.localisation_mapping = flatten_dict(self.localisation_mapping)
        self.mode = mode
        self.data_retreiver =  DatasetRetreiver(context=context, config=config)
        self.now = datetime.today()

        self.today = datetime.today().strftime(date_format)

    @timing
    def run(self):
        
        df = self.read_data()
        df = self.homogenize_localisation(df)
        df = self.deduce_country(df)
        df = self.remove_missing_values(df, important_cols=[self.name.total_description])
        # df = self.deduce_language(df)

        # homogenize prices to have comparison through geo & time
        dict_currencies = extract_currencies(liste_currency_paires)
        df_currencies = self.concatenate_currencies(dict_currencies, 
                                                    min_date=df[self.name.date].fillna(self.today).min())
        df = self.homogenize_currencies(df, df_currencies)
        df = self.remove_features(df, ["OPEN", "CLOSE"])
        df = self.add_execution_time(df)
        self.write_data(df)

        # save per_item same data 
        df = self.reduce_dim_to_per_item(df)
        self.write_data_per_item(df)
        
    def read_data(self):
        if self.mode == "history":
            df = self.data_retreiver.get_all_dataframes()
        elif self.mode == "new":
            df = self.data_retreiver.get_all_new_dataframes()
        else:
            raise Exception("EITHER NEW OR HISTORY MODE AVAILABLE")
        return df
    
    def write_data(self, df):
        if self.mode == "history":
            self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name,
                            if_exists="replace")
            
        elif self.mode == "new":
            self._log.info(f"Appending {df.shape} to the already existing history table {self.sql_table_name}")
            sql_values = tuple(df[self.name.id_unique].tolist())
            self.remove_rows_sql_data(values=sql_values,
                                      column=self.name.id_unique,
                                      table_name=self.sql_table_name)
            self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name,
                            if_exists="append")

            # TODO: remove files from auctions, detailed / items in new after all is appended
        else:
            raise Exception("EITHER NEW OR HISTORY MODE AVAILABLE")
        
    def write_data_per_item(self, df):
        if self.mode == "history":
            self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name_per_item,
                            if_exists="replace")
            
        elif self.mode == "new":
            self._log.info(f"Appending {df.shape} to the already existing history table {self.sql_table_name_per_item}")
            sql_values = tuple(df[self.name.id_item].tolist())
            self.remove_rows_sql_data(values=sql_values,
                                      column=self.name.id_item,
                                      table_name=self.sql_table_name_per_item)
            self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name_per_item,
                            if_exists="append")
        else:
            raise Exception("EITHER NEW OR HISTORY MODE AVAILABLE")

    @timing
    def concatenate_currencies(self, dict_currencies: Dict, 
                               min_date : str ="2000-01-01") -> pd.DataFrame:
        
        date_range = pd.DataFrame(pd.date_range(start=min_date, end=self.today), columns=[self.name.date])
        date_range[self.name.date] = date_range[self.name.date].dt.strftime("%Y-%m-%d")

        df_currencies = pd.DataFrame()
        for currency, data in dict_currencies.items():
            data[self.name.currency] = currency
            data.columns = [x.upper() for x in data.columns]
            data.rename(columns={"DATE" : self.name.date}, inplace=True)
            data = pd.merge(date_range, data, how="left", on=self.name.date, validate="1:1")

            for col in ["OPEN", "CLOSE", self.name.currency]:
                data[col] = data[col].bfill().ffill()

            df_currencies = pd.concat([df_currencies, data], axis=0)
        
        df_currencies = df_currencies.drop_duplicates([self.name.date, self.name.currency])

        return df_currencies


    @timing
    def homogenize_currencies(self, df: pd.DataFrame, 
                              df_currencies: pd.DataFrame) -> pd.DataFrame:
        
        # fill missing currencies
        df[self.name.currency] = np.where(df[self.name.currency].isnull()&df[self.name.country].isin(["FRANCE", "PAYS-BAS", "ITALIE"]),
                                                                                                     "EUR",
                                 np.where(df[self.name.currency].isnull()&df[self.name.country].isin(["CHINE"]), "CNY",
                                 np.where(df[self.name.currency].isnull()&df[self.name.country].isin(["UK"]), "GBP",
                                 np.where(df[self.name.currency].isnull()&df[self.name.country].isin(["USA"]), "USD", 
                                np.where(df[self.name.currency].isnull()&df[self.name.country].isin(["SUISSE"]), "CHF", 
                                np.where(df[self.name.currency].isnull()&df[self.name.country].isin(["AUSTRALIE"]), "AUD", 
                                         df[self.name.currency]))))))

        # two same chinese currency terms
        df[self.name.currency] = np.where(df[self.name.currency]=="RMB", "CNY", df[self.name.currency])
        df = df.merge(df_currencies, on=[self.name.date, self.name.currency], how="left", validate="m:1")

        old_currencies_coef = df[self.name.currency].map(fixed_eur_rate)
        df[self.name.currency_coef_eur] = np.where(df[self.name.currency] == "EUR" , 1,
                                        np.where(old_currencies_coef.notnull(), old_currencies_coef,
                                                df[["OPEN", "CLOSE"]].mean(axis=1))).clip(0, None)
        
        for new_col, col in [(self.name.eur_item_result, self.name.item_result), 
                             (self.name.eur_min_estimate, self.name.min_estimate), 
                             (self.name.eur_max_estimate, self.name.max_estimate)]:
            df[new_col] = (df[col]*df[self.name.currency_coef_eur]).round(0)

        return df 


    @timing
    def homogenize_localisation(self, df: pd.DataFrame) -> pd.DataFrame:
        
        df[self.name.type_sale] =(df[self.name.type_sale] + 1*df[self.name.localisation].isin(['www.aguttes.com',
                                'www.bonhams.com', 'www.christies.com',
                                'www.dawsonsauctions.co.uk', 'www.drouot.com',
                                'www.elmwoods.co.uk', 'www.geneve-encheres.ch',
                                'www.incanto.auction/it/asta-0216/design.asp',
                                'www.invaluable.com', 'www.kollerauctions.com',
                                'www.lambertzhao.com', 'www.millon.com',
                                'www.nathanmilleraste.com', 'www.online.aguttes.com',
                                'www.pastor-mdv.fr', 'www.piasa.fr', 'www.piguet.com',
                                'https://www.boisgirard-antonini.com/vente/aviation-3/',
                                'www.auktionshalle-cuxhaven.com',
                                'www.clarauction.com',
                                'www.rops-online.be', 'www.sothebys.com', 'www.venduehuis.com',
                                'www.vendurotterdam.nl', 'online', 'onlineonly.christies.com'])).clip(0,1)

        # clean localisation
        df[self.name.localisation] = df[self.name.localisation].str.lower()
        mapped_loc = df[self.name.localisation].map(self.localisation_mapping)
        df[self.name.localisation] = np.where(mapped_loc.notnull(), mapped_loc,
                                     np.where(df[self.name.localisation]=="nan", np.nan, 
                                            df[self.name.localisation]))
        df[self.name.localisation] = df[self.name.localisation].apply(lambda x: remove_accents(str(x)))

        return df

    @timing
    def deduce_country(self, df: pd.DataFrame) -> pd.DataFrame:
        clean_mapping =  {remove_accents(k) : v for k, v in self.country_mapping.items()}
        df[self.name.country] = df[self.name.localisation].map(clean_mapping)
        df[self.name.country] = np.where((df[self.name.country] != "nan")&(df[self.name.country].notnull()), df[self.name.country],
                                np.where(df[self.name.currency] == "GBP", "UK",
                                np.where(df[self.name.currency] == "CHF", "SUISSE",
                                np.where(df[self.name.currency] == "CAD", "CANADA",
                                np.where(df[self.name.currency] == "CNY", "CHINA",
                                np.where(df[self.name.currency] == "AUD", "AUSTRALIE",
                                np.where(df[self.name.currency] == "USD", "USA",
                                np.where(df[self.name.currency] == "EUR", "FRANCE", np.nan))))))))

        return df
    
    def deduce_language(self, df: pd.DataFrame) -> pd.DataFrame: # takes 4h....
        df["LANGUE"] = df[self.name.total_description].swifter.apply(lambda x: 
                                                    langid.classify(str(x)))
        df["TEXT_LEN"] = df[self.name.total_description].apply(lambda x: len(str(x)))
        return df
    
    def add_execution_time(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.name.executed_time] = self.now 
        return df
    
    @timing
    def reduce_dim_to_per_item(self, df):
        serie_list_pict = df[[self.name.id_item, self.name.id_picture]].groupby(self.name.id_item)[self.name.id_picture].apply(list)
        new_df = df.drop_duplicates(self.name.id_item)
        new_df = (
            new_df
                  .drop([self.name.id_unique, self.name.id_picture], axis=1)
                  .merge(serie_list_pict, 
                         left_on=self.name.id_item, 
                         right_index=True, 
                         how="left", 
                         validate="1:1")
                )
        return new_df