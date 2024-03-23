from typing import Dict
import numpy as np
import pandas as pd 
from typing import List
from datetime import datetime

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.constants.variables import (list_sellers, 
                                    liste_currency_paires, 
                                    fixed_eur_rate)

from src.datacrawl.transformers.TextCleaner import TextCleaner
from src.utils.utils_crawler import read_json
from src.utils.utils_dataframe import remove_accents
from src.utils.utils_currencies import extract_currencies

from omegaconf import DictConfig


class StepAgglomerateTextInfos(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)

        self.sql_table_name = self._config.cleaning.full_data_auction_houses
        self.path_mapping_country = self._config.cleaning.path_mapping_country
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.table_names = {}
        for seller in list_sellers:
            self.table_names[seller] = self.get_sql_db_name(seller)


    @timing
    def run(self):

        mapping_city_country = read_json(path=self.path_mapping_country)

        df = self.concatenate_sellers()
        df = self.keep_relevant_features(df)
        df = self.homogenize_localisation(df)
        df = self.deduce_country(df, mapping_country=mapping_city_country)
        df = self.homogenize_title(df)

        # homogenize prices to have comparison through geo & time
        dict_currencies = extract_currencies(liste_currency_paires)
        df_currencies = self.concatenate_currencies(dict_currencies)
        df = self.homogenize_currencies(df, df_currencies)

        self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name,
                            if_exists="replace")


    @timing
    def concatenate_sellers(self):
        final_df = pd.DataFrame()
        for seller in list_sellers: 
            df = pd.read_sql(self.table_names[seller], con=self._context.db_con)
            final_df = pd.concat([final_df, df], axis=0)
        return final_df

    @timing
    def keep_relevant_features(self, final_df):
        return final_df[[self.name.id_item,
                             self.name.lot, 
                             self.name.date,
                             self.name.hour,
                             self.name.item_title,
                             self.name.item_description,
                             self.name.min_estimate,
                             self.name.max_estimate,
                             self.name.item_result,
                             self.name.is_item_result,
                             self.name.currency,
                             self.name.id_picture,
                             self.name.localisation,
                             self.name.seller,
                             self.name.type_sale]]

    @timing
    def concatenate_currencies(self, df, dict_currencies):
        
        min_date = df[self.name.date].min()
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
    def homogenize_currencies(self, df, df_currencies):

        # two same chinese currency terms
        df[self.name.currency] = np.where(df[self.name.currency]=="RMB", "CNY", df[self.name.currency])
        df = df.merge(df_currencies, on=[self.name.date, self.name.currency], how="left", validate="m:1")

        old_currencies_coef = df[self.name.currency].map(fixed_eur_rate)
        df[self.name.currency_coef_eur] = np.where(df[self.name.currency] == "EUR" , 1,
                              np.where(old_currencies_coef.notnull(), old_currencies_coef,
                                       df[["OPEN", "CLOSE"]].mean(axis=1))).clip(0, None)
        
        for colname in [self.name.item_result, self.name.min_estimate, self.name.max_estimate]:
            df["EUR_" + colname] = (df[colname]*df[self.name.currency_coef_eur]).round(0)

        return df 


    @timing
    def homogenize_localisation(self, df):

        df[self.name.type_sale] = np.where(df[self.name.localisation].isin(['www.aguttes.com',
                                                'www.bonhams.com', 'www.christies.com',
                                                'www.dawsonsauctions.co.uk', 'www.drouot.com',
                                                'www.elmwoods.co.uk', 'www.geneve-encheres.ch',
                                                'www.incanto.auction/it/asta-0216/design.asp',
                                                'www.invaluable.com', 'www.kollerauctions.com',
                                                'www.lambertzhao.com', 'www.millon.com',
                                                'www.nathanmilleraste.com', 'www.online.aguttes.com',
                                                'www.pastor-mdv.fr', 'www.piasa.fr', 'www.piguet.com',
                                                'www.rops-online.be', 'www.sothebys.com', 'www.venduehuis.com',
                                                'www.vendurotterdam.nl', 'online', 'onlineonly.christies.com']), 
                                            1, df[self.name.type_sale])
        df[self.name.type_sale] = df[self.name.type_sale].fillna(0)

        df[self.name.localisation] = df[self.name.localisation].str.lower()
        df[self.name.localisation] = np.where(df[self.name.localisation].isin(['online', 'onlineonly.christies.com', "londres", "london (south kensigton)", 
                                                                "london", "www.nathanmilleraste.com", "www.lambertzhao.com", "www.bonhams.com", "www.sothebys.com", 
                                                                'www.dawsonsauctions.co.uk','www.elmwoods.co.uk']), "london",
                                    np.where(df[self.name.localisation].isin(['', "nan", '(mo)', '(ta)', '(vr)', '54623', '7']), np.nan,
                                    np.where(df[self.name.localisation].isin(['(anvers)', 'anvers']), 'anvers',
                                    np.where(df[self.name.localisation].isin(['alencon','alençon']), "alencon",
                                    np.where(df[self.name.localisation].isin(['athens', 'athènes']), "athènes",
                                    np.where(df[self.name.localisation].isin(['barcelona', 'barcelone']), "barcelone",
                                    np.where(df[self.name.localisation].isin(['bern', 'berne']), "berne", 
                                    np.where(df[self.name.localisation].isin(['bruxelles', 'www.rops-online.be']), "bruxelles",
                                    np.where(df[self.name.localisation].isin(['paris', "www.millon.com", 'www.online.aguttes.com', 'www.piasa.fr',
                                                                            'www.drouot.com', "www.piguet.com", 'www.aguttes.com',
                                                                            "https://www.boisgirard-antonini.com/vente/aviation-3/",
                                                                            "www.pastor-mdv.fr"]), "paris",
                                    np.where(df[self.name.localisation].isin(['bologna', 'bologne']), "bologne",
                                    np.where(df[self.name.localisation].isin(['basel', 'bâle']), "bâle",
                                    np.where(df[self.name.localisation].isin(['chambery', 'chambéry']), "chambéry",
                                    np.where(df[self.name.localisation].isin(['geneva', 'geneve', 'genova', 'www.geneve-encheres.ch', 
                                                                            'genève', 'genèves', "www.kollerauctions.com"]), "geneve",
                                    np.where(df[self.name.localisation].isin(['germany', 'berlin']), "berlin",
                                    np.where(df[self.name.localisation].isin(['hong kong', 'hong-kong', 'hongkong']), "hong-kong",
                                    np.where(df[self.name.localisation].isin(['levallois', 'levallois-perret']), 'levallois-perret',
                                    np.where(df[self.name.localisation].isin(['milan', 'milano', 'www.incanto.auction/it/asta-0216/design.asp']), "milan",
                                    np.where(df[self.name.localisation].isin(['roma', 'rome']), "rome",
                                    np.where(df[self.name.localisation].isin(['rosiere', 'rosière']), "rosière",
                                    np.where(df[self.name.localisation].isin(['saarbrucken', 'saarbrücken',]), "saarbrucken",
                                    np.where(df[self.name.localisation].isin(['vienna', 'vienne']), "vienne",
                                    np.where(df[self.name.localisation].isin(['zurich', 'zürich']), "zurich",
                                    np.where(df[self.name.localisation].isin(['www.venduehuis.com', 'la hague']), "la hague",
                                    np.where(df[self.name.localisation].isin(['www.invaluable.com', 'nouvelle orleans']), "nouvelle orleans",
                                    np.where(df[self.name.localisation].isin(['www.vendurotterdam.nl', 'rotterdam']), "rotterdam",
                                    np.where(df[self.name.localisation].isin(['hannut', 'hannut)', "(hannut)"]), "hannut",
                                            df[self.name.localisation] ))))))))))))))))))))))))))

        return df

    @timing
    def deduce_country(self, df, mapping_country):
        clean_mapping =  {remove_accents(k) : v for k, v in mapping_country.items()}

        df[self.name.localisation] = df[self.name.localisation].apply(lambda x: remove_accents(str(x)))
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
    def homogenize_title(self, df):

        df[self.name.item_title] = df[self.name.item_title].apply(lambda x : re.sub("^(\\d+\\. )", '', str(x)))
        df[self.name.item_title] = np.where(df[self.name.item_title] == "None", np.nan, 
                                            df[self.name.item_title])
        
        return df 
