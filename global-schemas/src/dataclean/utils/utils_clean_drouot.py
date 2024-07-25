import pandas as pd
import logging
import numpy as np
import locale
import re
import os

from src.dataclean.transformers.TextCleaner import TextCleaner
from src.context import Context
from src.utils.timing import timing
from src.constants.variables import DATE_FORMAT
from src.utils.utils_crawler import encode_file_name

from omegaconf import DictConfig


def clean_url_picture_list(x):
    try:
        return (
            re.findall('url\\("(.+?)"\\)', str(x))[0].replace(
                "size=small", "size=phare"
            )
            if "url(" in str(x)
            else str(x).replace("size=small", "size=phare")
        )
    except Exception:
        logging.error(x)
        return np.nan


class CleanDrouot(TextCleaner):

    def __init__(self, context: Context, config: DictConfig):

        super().__init__(context=context, config=config)
        locale.setlocale(locale.LC_ALL, "fr_FR")

    @timing
    def clean_auctions(self, df_auctions):
        df_auctions = df_auctions.drop_duplicates(
            [self.name.url_auction, self.name.auction_title, self.name.date]
        )
        df_auctions[self.name.id_auction] = df_auctions[self.name.url_auction].apply(
            lambda x: os.path.basename(x)
        )
        return df_auctions

    @timing
    def extract_hour_infos(self, df):
        df[self.name.date] = df[self.name.date].apply(
            lambda x: re.sub(r"\(.*?\)", "", str(x)).strip()
        )
        df[self.name.date] = pd.to_datetime(
            df[self.name.date], format="%A %d %B %Y - %H:%M"
        )
        df[self.name.hour] = df[self.name.date].dt.hour
        df[self.name.date] = df[self.name.date].dt.strftime(DATE_FORMAT)
        return df

    @timing
    def handle_type_of_sale(self, df):
        occurence = df[self.name.type_sale].unique()
        if len(occurence) == 2:
            df[self.name.type_sale] = 1 * (df[self.name.type_sale] == "Online")
        else:
            raise Exception(
                f"DROUOT DATAPREP for {self.name.type_sale} expects 2 single occurence, {occurence} found"
            )
        return df

    @timing
    def clean_items_per_auction(self, df):
        df[self.name.item_description] = df[self.name.item_infos]

        # clean localisation
        df[self.name.localisation] = np.where(
            df[self.name.place].isin(
                ["www.drouot.com", "Drouot Live ONLY - - -", "Vente Huis Clos -"]
            ),
            "Hotel Drouot - 75009 Paris",
            np.where(
                df[self.name.place].apply(lambda x: "www.setdart.com" in str(x)),
                "Arago, 346 - 08009 Barcelone, Espagne",
                np.where(
                    df[self.name.place] == "- , Luxembourg",
                    "XXX - 001 Luxembourg, Luxembourg",
                    np.where(
                        df[self.name.place] == "- , Suisse",
                        "XXX - 001 Genève, Suisse",
                        np.where(
                            df[self.name.place] == "- , Royaume-Uni",
                            "XXX - 001 London, Royaume uni",
                            df[self.name.place],
                        ),
                    ),
                ),
            ),
        )
        df[self.name.localisation] = df[self.name.localisation].apply(
            lambda x: str(x).split(" - ")[-1].split(",")[0].strip().split(" ")[-1]
        )
        df[self.name.localisation] = np.where(
            df[self.name.localisation].isin(["-", "- ,"]),
            np.nan,
            df[self.name.localisation].str.lower(),
        )

        # extract selling price and estimation
        df_results = self.get_splitted_infos(
            df[self.name.brut_estimate], index=df.index, sep="/"
        )
        df[self.name.brut_result], df[self.name.brut_estimate] = (
            df_results[0],
            df_results[1],
        )

        # get id_auction from file
        df[self.name.id_auction] = df[self.name.item_file].apply(
            lambda x: str(x).replace(".csv", "")
        )

        # handle type of sale and hours
        df = self.extract_hour_infos(df)
        df = self.handle_type_of_sale(df)

        return df

    @timing
    def clean_details_per_item(self, df):

        df[self.name.url_picture] = np.where(
            df[self.name.url_picture + "_DETAIL"].isnull(),
            df[self.name.url_picture].apply(lambda x: [x]),
            df[self.name.url_picture + "_DETAIL"],
        )
        # create id picture
        df = self.get_pictures_url_drouot(df)

        return df

    def naming_picture_drouot(self, x):
        return os.path.basename(str(x))

    def get_pictures_url_drouot(self, df_details, mode=None):

        if mode != "canvas":
            df_details = df_details.explode(self.name.url_picture)
            df_details[self.name.url_picture] = df_details[self.name.url_picture].apply(
                lambda x: clean_url_picture_list(x)
            )
            df_details[self.name.id_picture] = df_details[self.name.url_picture].apply(
                lambda x: self.naming_picture_drouot(x)
            )
        else:
            df_details = df_details.drop_duplicates("CURRENT_URL")
            df_details = df_details.loc[df_details[self.name.url_picture].isin([[]])]
            df_details[self.name.id_picture] = df_details["CURRENT_URL"].apply(
                lambda x: encode_file_name(os.path.basename(x))
            )
            df_details[self.name.url_picture] = df_details["CURRENT_URL"]

        return df_details
