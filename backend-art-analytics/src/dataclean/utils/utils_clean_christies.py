import pandas as pd
import numpy as np
import os

from src.context import Context
from src.dataclean.transformers.TextCleaner import TextCleaner
from src.utils.timing import timing
from src.constants.variables import date_format
from src.utils.utils_crawler import read_pickle, encode_file_name

from omegaconf import DictConfig


class CleanChristies(TextCleaner):

    def __init__(self, context: Context, config: DictConfig):

        super().__init__(context=context, config=config)
        self.root_path = self._config.crawling.root_path
        self.correction_urls_auction = (
            self.root_path + self._config.crawling["christies"].correction_urls_auction
        )

    @timing
    def clean_auctions(self, df_auctions):

        mapping_corr_urls_auction = read_pickle(path=self.correction_urls_auction)

        # URL auction clean
        df_auctions["CORRECTED_URL"] = df_auctions[self.name.url_auction].map(
            mapping_corr_urls_auction
        )
        corrected_id_auction = df_auctions["CORRECTED_URL"].apply(
            lambda x: str(x).split("/")[-1]
        )

        df_auctions[self.name.url_auction] = list(
            map(
                lambda x: x[:-1] if x[-1] == "/" else x,
                df_auctions[self.name.url_auction].tolist(),
            )
        )
        df_auctions[self.name.url_auction] = list(
            map(
                lambda x: os.path.basename(x),
                df_auctions[self.name.url_auction].tolist(),
            )
        )
        df_auctions[self.name.id_auction] = df_auctions[self.name.url_auction].apply(
            lambda x: str(x).split("-")[-1]
        )
        df_auctions[self.name.id_auction] = np.where(
            corrected_id_auction == "nan",
            df_auctions[self.name.id_auction],
            corrected_id_auction,
        )

        # LOCALISATION
        df_auctions[self.name.localisation] = list(
            map(
                lambda x: str(x).replace("EVENT LOCATION\n", ""),
                df_auctions[self.name.localisation].tolist(),
            )
        )
        df_auctions[self.name.date] = pd.to_datetime(
            df_auctions[self.name.auction_file], format="month=%m&year=%Y.csv"
        )
        df_auctions[self.name.date] = df_auctions[self.name.date].dt.strftime(
            date_format
        )

        return df_auctions.drop(["CORRECTED_URL"], axis=1)

    @timing
    def clean_items_per_auction(self, df):

        df = df.loc[df[self.name.url_full_detail].notnull()]
        df[self.name.item_file] = df[self.name.item_file].apply(
            lambda x: str(x).split("&")[0].replace(".csv", "")
        )
        df[self.name.lot] = df[self.name.lot].str.replace("LOT ", "")
        df[self.name.url_auction] = df[self.name.url_auction].apply(
            lambda x: x.split("/?loadall")[0]
        )
        df[self.name.url_auction] = list(
            map(
                lambda x: x[:-1] if x[-1] == "/" else x,
                df[self.name.url_auction].tolist(),
            )
        )
        df[self.name.url_auction] = list(
            map(lambda x: os.path.basename(x), df[self.name.url_auction].tolist())
        )
        df[self.name.id_auction] = df[self.name.url_auction].apply(
            lambda x: str(x).split("-")[-1]
        )

        assert df[self.name.item_file].nunique() == df[self.name.id_auction].nunique()

        # type sale
        if self.name.type_sale not in df.columns:
            df[self.name.type_sale] = 0

        # date, place, maison
        sale = self.get_splitted_infos(
            df[self.name.item_infos].fillna(""), index=df.index, sep="\n"
        )
        df[self.name.item_title] = sale[1]
        df[self.name.item_description] = sale[2]

        return df

    @timing
    def clean_details_per_item(self, df_details, mode=None):
        df_details = df_details.explode(self.name.url_picture)
        df_details[self.name.url_picture] = np.where(
            df_details[self.name.url_picture].apply(
                lambda x: str(x) == "" or str(x) == "nan"
            ),
            np.nan,
            df_details[self.name.url_picture],
        )
        df_details[self.name.id_picture] = df_details[self.name.url_picture].apply(
            lambda x: self.naming_picture_christies(x)
        )
        return df_details

    def naming_picture_christies(self, x):
        return encode_file_name(os.path.basename(str(x)))
