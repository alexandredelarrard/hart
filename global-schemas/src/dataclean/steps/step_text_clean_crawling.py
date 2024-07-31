from omegaconf import DictConfig
import numpy as np
import pandas as pd
from typing import Dict
import re
import langid
import locale
from datetime import datetime

from src.context import Context
from src.dataclean.transformers.TextCleaner import TextCleaner
from src.utils.timing import timing
from src.schemas.crawling_schemas import Auctions, Items, Details
from src.schemas.crawling_cleaning import AllItems
from src.utils.utils_dataframe import remove_accents, flatten_dict
from src.utils.utils_currencies import extract_currencies

from src.constants.variables import (
    LOCALISATION,
    MAP_MONTH,
    LIST_CURRENCY_PAIRS,
    FIXED_EUR_RATE,
    DATE_FORMAT,
)


class StepCleanCrawling(TextCleaner):

    def __init__(self, context: Context, config: DictConfig):

        super().__init__(context=context, config=config)

        self.sql_details_table = Details.__tablename__
        self.sql_auction_table = Auctions.__tablename__
        self.sql_items_table = Items.__tablename__
        self.sql_output_table_name = AllItems.__tablename__

        self.localisation_mapping = self._config.cleaning.mapping.localisation
        self.localisation_mapping = flatten_dict(self.localisation_mapping)
        self.country_mapping = self._config.cleaning.mapping.country

        self.cols_items = [
            self.name.low_id_item,
            self.name.low_id_auction,
            self.name.url_full_detail,
            self.name.lot,
            self.name.item_title,
            self.name.item_description,
            self.name.seller,
            self.name.estimate,
            self.name.result,
        ]
        self.cols_details = [
            self.name.low_id_item,
            self.name.detailed_title,
            self.name.detailed_description,
            self.name.url_picture,
            self.name.id_picture,
            self.name.estimate,
        ]

        self.list_cols_items = ", ".join([f'"{x}"' for x in self.cols_items])
        self.list_cols_details = ", ".join([f'"{x}"' for x in self.cols_details])
        self.today = datetime.today().strftime(DATE_FORMAT)

    @timing
    def run(self):

        # # CLEAN ITEMS
        df = self.read_sql_data(
            f"""
                WITH filtered_items AS (
                    SELECT items.{self.name.low_id_item},
                        items.{self.name.low_id_auction},
                        items."{self.name.url_full_detail}",
                        items."{self.name.lot}",
                        items."{self.name.item_title}",
                        items."{self.name.item_description}",
                        items."{self.name.seller}",
                        items."{self.name.estimate}",
                        items."{self.name.result}"
                    FROM {self.sql_items_table} AS items
                    LEFT JOIN (
                        SELECT {self.name.low_id_item}
                        FROM "{self.sql_output_table_name}"
                        ) AS all_items
                    ON items.{self.name.low_id_item} = all_items.{self.name.low_id_item}
                    WHERE all_items.{self.name.low_id_item} IS NULL
                )
                SELECT filtered_items.{self.name.low_id_item},
                    filtered_items.{self.name.low_id_auction},
                    filtered_items."{self.name.url_full_detail}",
                    filtered_items."{self.name.lot}",
                    filtered_items."{self.name.item_title}",
                    filtered_items."{self.name.item_description}",
                    filtered_items."{self.name.seller}",
                    CASE
                        WHEN filtered_items."{self.name.estimate}" IS NULL THEN details."{self.name.estimate}"
                        ELSE filtered_items."{self.name.estimate}"
                    END AS "{self.name.estimate}",
                    CASE
                        WHEN filtered_items."{self.name.result}" IS NULL THEN details."{self.name.result}"
                        ELSE filtered_items."{self.name.result}"
                    END AS "{self.name.result}",
                    details."{self.name.detailed_title}",
                    details."{self.name.detailed_description}",
                    details."{self.name.url_picture}",
                    details."{self.name.id_picture}"
                FROM filtered_items
                LEFT JOIN (
                    SELECT {self.list_cols_details}, "{self.name.result}"
                    FROM {self.sql_details_table}
                ) AS details
                ON details.{self.name.low_id_item} = filtered_items.{self.name.low_id_item}
                WHERE filtered_items."{self.name.result}" IS NOT NULL OR filtered_items."{self.name.estimate}" IS NOT NULL
            """
        )

        df = self.clean_lots(df)
        df = self.extract_estimates(df)  # text cleaner
        df = self.extract_currency(df)  # text cleaner
        df = self.clean_estimations(
            df,
            [
                "this lot has been withdrawn from auction",
                "estimate on request",
                "estimate unknown",
                "price realised",
                "estimate upon request",
                "résultat : non communiqué",
                "estimation : manquante",
            ],
        )
        df = self.remove_missing_values(df, [self.name.item_result])
        df = self.clean_description(df)

        # clean and merge with auction table
        df_auctions = self.read_sql_data(self.sql_auction_table)
        df_auctions = self.deduce_type_sale(df_auctions)
        df_auctions = self.clean_date_formats(df_auctions)
        df_auctions = self.clean_auctions(df_auctions)
        df = df.merge(
            df_auctions,
            on=["id_auction", "SELLER"],
            how="left",
            validate="m:1",
            suffixes=("", "_AUCTION"),
        )
        df = self.deduce_country(df)

        # post processing
        df = self.clean_text_description(df)
        dict_currencies = extract_currencies(LIST_CURRENCY_PAIRS)
        df_currencies = self.concatenate_currencies(
            dict_currencies, min_date=df[self.name.date].fillna(self.today).min()
        )
        df = self.homogenize_currencies(df, df_currencies)
        df = self.remove_features(df, ["OPEN", "CLOSE"])
        df = self.homogenize_lot_number(df)
        df = self.add_execution_time(df)
        df = self.remove_missing_values(df, [self.name.total_description])

        # keep important cols
        df = df[
            [
                self.name.low_id_item,
                self.name.low_id_auction,
                self.name.id_picture,
                self.name.date,
                self.name.localisation,
                self.name.lot,
                self.name.seller,
                self.name.house,
                self.name.type_sale,
                self.name.url_auction,
                self.name.url_full_detail,
                self.name.auction_title,
                self.name.detailed_title,
                self.name.total_description,
                self.name.currency,
                self.name.item_result,
                self.name.min_estimate,
                self.name.max_estimate,
                self.name.eur_item_result,
                self.name.eur_min_estimate,
                self.name.eur_max_estimate,
                self.name.is_item_result,
                self.name.executed_time,
            ]
        ]

        # remove existing ids
        self.remove_rows_sql_data(
            values=df[self.name.low_id_item].tolist(),
            column=self.name.low_id_item,
            table_name=self.sql_output_table_name,
        )

        # SAVE ITEMS ENRICHED
        self.write_sql_data(
            dataframe=df, table_name=self.sql_output_table_name, if_exists="append"
        )

        return df

    @timing
    def clean_lots(self, df: pd.DataFrame) -> pd.DataFrame:

        # clean lot number
        df[self.name.lot] = df[self.name.lot].str.replace("LOT ", "")
        df[self.name.lot] = df[self.name.lot].apply(lambda x: self.clean_each_lot(x))
        df[self.name.lot] = np.where(
            df[self.name.lot].apply(lambda x: not str(x).isdigit()),
            np.nan,
            df[self.name.lot],
        )

        return df

    @timing
    def clean_auctions(self, df_auctions: pd.DataFrame) -> pd.DataFrame:

        # localisation
        df_auctions[self.name.localisation] = np.where(
            df_auctions[self.name.seller] == "drouot",
            self.localisation_drouot(df_auctions[self.name.localisation]),
            np.where(
                df_auctions[self.name.seller] == "millon",
                self.localisation_millon(df_auctions[self.name.localisation]),
                np.where(
                    df_auctions[self.name.seller] == "christies",
                    self.localisation_christies(df_auctions[self.name.localisation]),
                    np.where(
                        df_auctions[self.name.seller] == "sothebys",
                        self.get_list_element_from_text(
                            df_auctions[self.name.date], liste=LOCALISATION
                        ),
                        None,
                    ),
                ),
            ),
        )

        # mapping to loc file
        df_auctions[self.name.localisation] = df_auctions[
            self.name.localisation
        ].str.lower()
        mapped_loc = df_auctions[self.name.localisation].map(self.localisation_mapping)
        df_auctions[self.name.localisation] = np.where(
            mapped_loc.notnull(), mapped_loc, df_auctions[self.name.localisation]
        )
        df_auctions[self.name.localisation] = np.where(
            df_auctions[self.name.localisation].isin([np.nan, None, "nan"]),
            None,
            df_auctions[self.name.localisation],
        )
        df_auctions[self.name.localisation] = df_auctions[self.name.localisation].apply(
            lambda x: remove_accents(str(x))
        )

        return df_auctions

    def clean_date_formats(self, df_auctions):

        # date
        df_auctions[self.name.date] = df_auctions[
            [self.name.date, self.name.seller]
        ].apply(lambda x: self.clean_date(x), axis=1)
        df_auctions[self.name.hour] = np.where(
            df_auctions[self.name.date].dt.hour == 0,
            np.nan,
            df_auctions[self.name.date].dt.hour,
        )
        df_auctions[self.name.date] = df_auctions[self.name.date].dt.strftime(
            DATE_FORMAT
        )
        return df_auctions

    def localisation_drouot(self, loc_serie):

        # clean localisation
        loc_serie = np.where(
            loc_serie.isin(
                ["www.drouot.com", "Drouot Live ONLY - - -", "Vente Huis Clos -"]
            ),
            "Hotel Drouot - 75009 Paris",
            np.where(
                loc_serie.apply(lambda x: "www.setdart.com" in str(x)),
                "Arago, 346 - 08009 Barcelone, Espagne",
                np.where(
                    loc_serie == "- , Luxembourg",
                    "XXX - 001 Luxembourg, Luxembourg",
                    np.where(
                        loc_serie == "- , Suisse",
                        "XXX - 001 Genève, Suisse",
                        np.where(
                            loc_serie == "- , Royaume-Uni",
                            "XXX - 001 London, Royaume uni",
                            np.where(
                                loc_serie == "- , Autriche",
                                "XXX - 001 Vienne, Autriche",
                                loc_serie,
                            ),
                        ),
                    ),
                ),
            ),
        )
        loc_serie = pd.Series(loc_serie).apply(
            lambda x: str(x).split(" - ")[-1].split(",")[0].strip().split(" ")[-1]
        )
        loc_serie = np.where(
            loc_serie.isin(["-", "- ,"]),
            np.nan,
            loc_serie.str.lower(),
        )
        return loc_serie

    def localisation_christies(self, loc_serie):
        loc_serie = list(
            map(
                lambda x: str(x).replace("EVENT LOCATION\n", ""),
                loc_serie.tolist(),
            )
        )
        return loc_serie

    def localisation_millon(self, loc_serie):

        loc_serie = np.where(
            loc_serie.isin(
                [
                    "NICE",
                    "NICE, 51 RUE BEAUMONT, 06300 NICE",
                    "51 RUE BEAUMONT, 06300 NICE",
                    "NICE, 3 PLACE FRANKLIN",
                    "3 PLACE FRANKLIN, 06000 - NICE",
                ]
            ),
            "nice",
            np.where(
                loc_serie.isin(["NANTES"]),
                "nantes",
                np.where(
                    loc_serie.isin(
                        [
                            "NEUILLY-SUR-MARNE",
                            "NEULLY-SUR-MARNE",
                            "116 BOULEVARD LOUIS-ARMAND, NEUILLY-SUR-MARNE 93330",
                        ]
                    ),
                    "neuilly-sur-marne",
                    np.where(
                        loc_serie.isin(["LYON VENTE"]),
                        "lyon",
                        np.where(
                            loc_serie.isin(
                                [
                                    "LES FRANCISCAINES - DEAUVILLE",
                                    "CENTRE INTERNATIONAL DEAUVILLE CID | PALAIS DES CONGRÈS DE DEAUVILLE_ SALON ART SHOPPING",
                                ]
                            ),
                            "deauville",
                            np.where(
                                loc_serie.isin(["LA CROIX-VALMER"]),
                                "croix-valmer",
                                "paris",
                            ),
                        ),
                    ),
                ),
            ),
        )
        return loc_serie

    def clean_date(self, row: str) -> str:

        seller = row["SELLER"]
        date_str = row["AUCTION_DATE"]

        if not date_str or date_str == "":
            return None

        if seller == "drouot":
            locale.setlocale(locale.LC_TIME, "fr_FR")
            date_str = re.sub(r"\(.*?\)", "", str(date_str)).strip()
            return pd.to_datetime(date_str, format="%A %d %B %Y - %H:%M")
        elif seller == "christies":
            locale.setlocale(locale.LC_TIME, "en_US")

            if "Event" in date_str:
                date_str = date_str.split("\n")[-1]
                if " – " in date_str:
                    date_str = date_str.split(" – ")[-1]
                date_str = date_str + " 2024"
            return self.try_multiple_formats(
                date_str, ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d %b %Y", "%d %B %Y"]
            )

        elif seller == "sothebys":
            try:
                locale.setlocale(locale.LC_TIME, "en_US")
                date_str = str(date_str).split("•")[0].strip()
                date_str = str(date_str).split("|")[0].strip().split("–")[-1]
                return self.try_multiple_formats(date_str, ["%d %B %Y", "%B %Y"])
            except Exception:
                pass
        elif seller == "millon":
            locale.setlocale(locale.LC_TIME, "fr_FR")
            if date_str == "VENTE EN LIGNE":
                return None
            date_str = date_str.split(" - ")
            if len(date_str) == 2:
                date_str = date_str[-1]
            elif len(date_str) == 3:
                date_str = date_str[1]
            else:
                date_str = date_str[0]

            x = date_str.split(" ")
            try:
                if len(x) == 3:
                    if "H" in x[2]:
                        match = re.match(r"([A-Z]+)(\d+H\d+)", x[2], re.IGNORECASE)
                        month_part = match.group(1)
                        time_part = match.group(2)
                        date_str = " ".join(
                            [x[1], x[2], MAP_MONTH[month_part], time_part, "2024"]
                        )
                    else:
                        x = (date_str + " 2024 00H00").split(" ")
                        date_str = " ".join([x[1], MAP_MONTH[x[2]], x[3], x[4]])
                elif len(x) == 4:
                    if "H" in x[3]:
                        x = (date_str + " 2024").split(" ")
                        date_str = " ".join([x[1], MAP_MONTH[x[2]], x[4], x[3]])
                    else:
                        x = (date_str + " 00H00").split(" ")
                        date_str = " ".join([x[1], MAP_MONTH[x[2]], x[3], x[4]])
                else:
                    date_str = " ".join([x[1], MAP_MONTH[x[2]], x[3], x[4]])
                return pd.to_datetime(date_str, format="%d %B %Y %HH%M")
            except Exception:
                return np.nan
        else:
            return np.nan

    def clean_each_lot(self, x: str) -> str:
        if str(x).isdigit():
            return x

        if ". lot n°" in str(x):
            return re.sub("(\\d+). lot n°", "", x)
        elif "test" in str(x).lower() or x == None or str(x) == "":
            return np.nan
        else:  # sothebys
            x = str(x).split(".")[0]
            x = str(x).split(" ")[0]
            x = re.sub("[a-zA-Z]", "", str(x))
            return x

    @timing
    def deduce_country(self, df: pd.DataFrame) -> pd.DataFrame:
        clean_mapping = {remove_accents(k): v for k, v in self.country_mapping.items()}
        df[self.name.country] = df[self.name.localisation].map(clean_mapping)
        df[self.name.country] = np.where(
            (df[self.name.country] != "nan") & (df[self.name.country].notnull()),
            df[self.name.country],
            np.where(
                df[self.name.currency] == "GBP",
                "UK",
                np.where(
                    df[self.name.currency] == "CHF",
                    "SUISSE",
                    np.where(
                        df[self.name.currency] == "CAD",
                        "CANADA",
                        np.where(
                            df[self.name.currency] == "CNY",
                            "CHINA",
                            np.where(
                                df[self.name.currency] == "AUD",
                                "AUSTRALIE",
                                np.where(
                                    df[self.name.currency] == "USD",
                                    "USA",
                                    np.where(
                                        df[self.name.currency] == "EUR",
                                        "FRANCE",
                                        np.nan,
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )

        return df

    def deduce_type_sale(self, df_auctions):

        df_auctions[self.name.type_sale] = (
            1
            * df_auctions[self.name.localisation].isin(
                [
                    "www.aguttes.com",
                    "www.bonhams.com",
                    "www.christies.com",
                    "www.dawsonsauctions.co.uk",
                    "www.drouot.com",
                    "www.elmwoods.co.uk",
                    "www.geneve-encheres.ch",
                    "www.incanto.auction/it/asta-0216/design.asp",
                    "www.invaluable.com",
                    "www.kollerauctions.com",
                    "www.lambertzhao.com",
                    "www.millon.com",
                    "www.nathanmilleraste.com",
                    "www.online.aguttes.com",
                    "www.pastor-mdv.fr",
                    "www.piasa.fr",
                    "www.artprecium.com",
                    "www.piguet.com",
                    "https://www.boisgirard-antonini.com/vente/aviation-3/",
                    "www.auktionshalle-cuxhaven.com",
                    "www.clarauction.com",
                    "www.rops-online.be",
                    "www.sothebys.com",
                    "www.venduehuis.com",
                    "www.vendurotterdam.nl",
                    "online",
                    "onlineonly.christies.com",
                ]
            )
        ).clip(0, 1)

        return df_auctions

    @timing
    def concatenate_currencies(
        self, dict_currencies: Dict, min_date: str = "2000-01-01"
    ) -> pd.DataFrame:

        date_range = pd.DataFrame(
            pd.date_range(start=min_date, end=self.today), columns=[self.name.date]
        )
        date_range[self.name.date] = date_range[self.name.date].dt.strftime("%Y-%m-%d")

        df_currencies = pd.DataFrame()
        for currency, data in dict_currencies.items():
            data[self.name.currency] = currency
            data.columns = [x.upper() for x in data.columns]
            data.rename(columns={"DATE": self.name.date}, inplace=True)
            data = pd.merge(
                date_range, data, how="left", on=self.name.date, validate="1:1"
            )

            for col in ["OPEN", "CLOSE", self.name.currency]:
                data[col] = data[col].bfill().ffill()

            df_currencies = pd.concat([df_currencies, data], axis=0)

        df_currencies = df_currencies.drop_duplicates(
            [self.name.date, self.name.currency]
        )

        return df_currencies

    @timing
    def homogenize_currencies(
        self, df: pd.DataFrame, df_currencies: pd.DataFrame
    ) -> pd.DataFrame:

        # fill missing currencies
        df[self.name.currency] = np.where(
            df[self.name.currency].isnull()
            & df[self.name.country].isin(["FRANCE", "PAYS-BAS", "ITALIE"]),
            "EUR",
            np.where(
                df[self.name.currency].isnull() & df[self.name.country].isin(["CHINE"]),
                "CNY",
                np.where(
                    df[self.name.currency].isnull()
                    & df[self.name.country].isin(["UK"]),
                    "GBP",
                    np.where(
                        df[self.name.currency].isnull()
                        & df[self.name.country].isin(["USA"]),
                        "USD",
                        np.where(
                            df[self.name.currency].isnull()
                            & df[self.name.country].isin(["SUISSE"]),
                            "CHF",
                            np.where(
                                df[self.name.currency].isnull()
                                & df[self.name.country].isin(["AUSTRALIE"]),
                                "AUD",
                                df[self.name.currency],
                            ),
                        ),
                    ),
                ),
            ),
        )

        # two same chinese currency terms
        df[self.name.currency] = np.where(
            df[self.name.currency] == "RMB", "CNY", df[self.name.currency]
        )
        df = df.merge(
            df_currencies,
            on=[self.name.date, self.name.currency],
            how="left",
            validate="m:1",
        )

        old_currencies_coef = df[self.name.currency].map(FIXED_EUR_RATE)
        df[self.name.currency_coef_eur] = np.where(
            df[self.name.currency] == "EUR",
            1,
            np.where(
                old_currencies_coef.notnull(),
                old_currencies_coef,
                df[["OPEN", "CLOSE"]].mean(axis=1),
            ),
        ).clip(0, None)

        for new_col, col in [
            (self.name.eur_item_result, self.name.item_result),
            (self.name.eur_min_estimate, self.name.min_estimate),
            (self.name.eur_max_estimate, self.name.max_estimate),
        ]:
            df[new_col] = (df[col] * df[self.name.currency_coef_eur]).round(0)

        return df

    def deduce_language(self, df: pd.DataFrame) -> pd.DataFrame:  # takes 4h....
        df["LANGUE"] = df[self.name.total_description].swifter.apply(
            lambda x: langid.classify(str(x))
        )
        df["TEXT_LEN"] = df[self.name.total_description].apply(lambda x: len(str(x)))
        return df

    def add_execution_time(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.name.executed_time] = datetime.now()
        return df
