from typing import Dict
import numpy as np
import pandas as pd 
from typing import List
from datetime import datetime
import swifter
import re 
import langid

from src.context import Context
from src.utils.timing import timing
from src.constants.variables import (liste_currency_paires, 
                                    fixed_eur_rate,
                                    date_format)

from src.datacrawl.transformers.TextCleaner import TextCleaner
from src.utils.utils_dataframe import (remove_accents,
                                       remove_punctuation,
                                       flatten_dict)
from src.utils.utils_currencies import extract_currencies

from omegaconf import DictConfig


class StepAgglomerateTextInfos(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)

        self.sql_table_name = self._config.cleaning.full_data_auction_houses
        self.country_mapping  = self._config.cleaning.mapping.country
        self.localisation_mapping = self._config.cleaning.mapping.localisation

        self.today = datetime.today().strftime(date_format)

    @timing
    def run(self):

        df = self.get_data()
        df = self.homogenize_localisation(df)
        df = self.deduce_country(df)
        df = self.homogenize_text(df)
        df = self.create_total_description(df)
        df = self.remove_missing_values(df, important_cols=[self.name.total_description])
        # df = self.deduce_language(df)

        # homogenize prices to have comparison through geo & time
        dict_currencies = extract_currencies(liste_currency_paires)
        df_currencies = self.concatenate_currencies(dict_currencies, 
                                                    min_date=df[self.name.date].min())
        df = self.homogenize_currencies(df, df_currencies)
        df = self.remove_features(df, ["OPEN", "CLOSE"])

        self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name,
                            if_exists="replace")
        
        return df

    @timing
    def get_data(self)-> pd.DataFrame:
        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_sellers_dataframe"))
        formatted_query = self.sql_queries.format_query(
                raw_query,
                {
                    "drouot_name": self._config.cleaning.drouot.origine_table_name,
                    "christies_name": self._config.cleaning.christies.origine_table_name,
                    "sothebys_name": self._config.cleaning.sothebys.origine_table_name,
                    "id_item": self.name.id_item,
                    "id_picture": self.name.id_picture,
                    "lot": self.name.lot,
                    "date": self.name.date,
                    "localisation": self.name.localisation,
                    "seller": self.name.seller,
                    "type_sale": self.name.type_sale,
                    "url_full_detail": self.name.url_full_detail,
                    "auction_title": self.name.auction_title,
                    "item_title": self.name.item_title,
                    "detailed_title": self.name.detailed_title,
                    "item_description": self.name.item_description,
                    "detailed_description": self.name.detailed_description,
                    "min_estimate": self.name.min_estimate,
                    "max_estimate": self.name.max_estimate,
                    "item_result": self.name.item_result,
                    "is_item_result": self.name.is_item_result,
                    "currency": self.name.currency
                },
            )

        # 3. Fetch results
        self._log.info(formatted_query)
        return self.read_sql_data(formatted_query)

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
        
        df[self.name.type_sale] =1*(df[self.name.localisation].isin(['www.aguttes.com',
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
                                'www.vendurotterdam.nl', 'online', 'onlineonly.christies.com']))

        # clean localisation
        self.localisation_mapping = flatten_dict(self.localisation_mapping)
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

    @timing
    def homogenize_text(self, df: pd.DataFrame) -> pd.DataFrame:

        # detailed description cleaning 
        for col in [self.name.item_description, self.name.detailed_description,
                    self.name.item_title, self.name.detailed_title]:
            df[col] = np.where(df[col].str.lower().isin([
                                    '', '1 ^,,^^,,^','2 ^,,^^,,^','1 ^"^^"^',
                                    '1 ^,,^', '3 ^,,^^,,^','6 ^,,^','2 ^,,^',
                                    '3 ^,,^','5 ^,,^^,,^', '4 ^,,^^,,^',
                                    '4 ^,,^', 'size 52.', '1 ^,,^^,,^ per dozen',
                                    '10 ^,,^^,,^', 'non venu', '.']), np.nan, 
                            df[col])
            
            df[col] = df[col].swifter.apply(lambda x: self.clean_description(x))
            df[col] = np.where(df[col].isin(["None","", "nan"]), np.nan, df[col])
        
        return df
    
    def deduce_language(self, df: pd.DataFrame) -> pd.DataFrame: # takes 4h....
        df["LANGUE"] = df[self.name.total_description].swifter.apply(lambda x: 
                                                    langid.classify(str(x)))
        df["TEXT_LEN"] = df[self.name.total_description].apply(lambda x: len(str(x)))
        return df
    
    @timing
    def create_total_description(self, df: pd.DataFrame) -> pd.DataFrame:

        df[self.name.total_description] = np.where(df[self.name.detailed_description].notnull(),
                                                   df[self.name.detailed_description],
                                                   df[self.name.item_description])
        
        df[self.name.total_description] = np.where(df[self.name.total_description].isnull(),
                                                   df[self.name.item_description],
                                                   df[self.name.total_description])
        
        df[self.name.total_description] = np.where(df[self.name.total_description].isnull(),
                                                   df[self.name.item_title],
                                                   df[self.name.total_description])

        # add title to desc if not in desc
        function_clean = lambda x: remove_punctuation(re.sub(" +", " ", str(x).lower().replace("\n"," "))).strip()
        # item_desc_in_desc =  df[[self.name.item_description, 
        #                    self.name.total_description]].swifter.apply(lambda x: function_clean(x[0]) in function_clean(x[1]), axis=1)
        
        title_in_desc = df[[self.name.item_title, 
                           self.name.total_description]].swifter.apply(lambda x: function_clean(x[0]) in function_clean(x[1]), axis=1)
        df[self.name.total_description] = np.where((~title_in_desc)&(df[self.name.item_title].notnull()),
                                                   df[self.name.item_title] + ". " + df[self.name.total_description].fillna(""),
                                                   df[self.name.total_description])

        return df 
    
    
    def clean_description(self, x :str) -> str :
    
        x = self.remove_lot_number(x)
        x = self.remove_estimate(x)
        x = self.remove_dates_in_parenthesis(x)
        x = self.clean_dimensions(x)
        x = self.clean_hight(x)
        x = self.clean_shorten_words(x)
        x = self.remove_spaces(x)
        x = self.remove_rdv(x)

        return x