from omegaconf import DictConfig
import os
import re
import numpy as np

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling
from src.utils.utils_crawler import (
    encode_file_name,
)
from src.schemas.crawling_schemas import Items, Details


class StepCrawlingDetails(Crawling):

    def __init__(
        self,
        context: Context,
        config: DictConfig,
        threads: int,
        seller: str = "christies",
    ):

        self.seller = seller
        self.sql_items_table_raw = Items.__tablename__
        self.sql_details_table_raw = Details.__tablename__

        kwargs = {}
        if "crawler_infos" in config.crawling[self.seller].detailed.keys():
            kwargs = config.crawling[self.seller].detailed["crawler_infos"]

        # initialize crawler as queue saving
        super().__init__(
            context=context,
            config=config,
            threads=threads,
            kwargs=kwargs,
        )

        self.detailed_infos = self._config.crawling[self.seller]["detailed"]

    # second crawling step  to get list of pieces per auction
    def get_list_items_to_crawl(self):

        # ITEMS
        df_items = self.read_sql_data(
            f"""SELECT DISTINCT items.\"{self.name.url_full_detail}\"
                FROM {self.sql_items_table_raw} as items
                LEFT JOIN (
                    SELECT {self.name.low_id_item}
                    FROM {self.sql_details_table_raw}
                    WHERE \"{self.name.seller}\"='{self.seller}'
                ) as details
                ON items.{self.name.low_id_item} = details.{self.name.low_id_item}
                WHERE items.\"{self.name.seller}\"='{self.seller}'
                    AND details.{self.name.low_id_item} IS NULL"""
        )
        to_crawl = df_items[self.name.url_full_detail].tolist()

        self._log.info(f"Nbr detailed items To crawl : {len(to_crawl)}")

        return to_crawl

    def crawl_iteratively_sothebys_detail(self, driver, config):
        url = driver.current_url
        infos = []
        if "/en/buy/" in url:
            infos = self.crawl_iteratively(driver, config.buy_url)
        elif "/en/auctions" in url:
            infos = self.crawl_iteratively(driver, config.auctions_url)
        else:
            self._log.warning(f"Could not crawl url {url} for {self.seller}")

        return infos

    def clean_url_pictures(self, x):

        try:
            if "url(" in str(x):
                x = re.findall('url\\("(.+?)"\\)', str(x))[0].replace(
                    "size=small", "size=phare"
                )
            else:
                x = str(x).replace("size=small", "size=phare")
                x = x.split("\n")[0].split(" ")[0]
                return x

        except Exception:
            self._log.error(x)
            return np.nan

    def crawling_details_function(self, driver):
        try:
            infos = eval(
                f"self.crawl_iteratively_{self.seller}_detail(driver=driver, config=self.detailed_infos)"
            )
        except Exception as e:
            self._log.debug(e)
            infos = self.crawl_iteratively(driver=driver, config=self.detailed_infos)

        if len(infos) == 1:
            row = infos[0]

            try:
                new_result = Details(
                    id_item=encode_file_name(row["CURRENT_URL"]),
                    URL_FULL_DETAILS=row["CURRENT_URL"],
                    DETAIL_TITLE=(
                        row[self.name.detailed_title]
                        if self.name.detailed_title in row.keys()
                        else None
                    ),
                    DETAIL_DESCRIPTION=(
                        row[self.name.detailed_description]
                        if self.name.detailed_description in row.keys()
                        else None
                    ),
                    ESTIMATE=(
                        row[self.name.estimate]
                        if self.name.estimate in row.keys()
                        else None
                    ),
                    RESULT=(
                        row[self.name.result]
                        if self.name.result in row.keys()
                        else None
                    ),
                    SELLER=self.seller,
                    URL_PICTURE=[
                        self.clean_url_pictures(x) for x in row[self.name.url_picture]
                    ],
                    ID_PICTURE=[
                        encode_file_name(os.path.basename(str(x)))
                        for x in row[self.name.url_picture]
                        if x not in ["", "nan", None]
                    ],
                )
                self.insert_raw_to_table(
                    unique_id_col=self.name.low_id_item,
                    row_dict=new_result.dict(),
                    table_name=self.sql_details_table_raw,
                )

            except Exception as e:
                self._log.error(f"Something wrong happened {e}")

        return driver, infos
