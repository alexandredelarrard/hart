from omegaconf import DictConfig
import re
import numpy as np

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling
from src.utils.utils_crawler import (
    encode_file_name,
)
from src.schemas.crawling_schemas import Items, Details, Pictures
from src.constants.variables import BLACK_LIST_ID_PICTURE


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
        self.sql_pictures_table_raw = Pictures.__tablename__
        self.root_url = f"https://www.{self.seller}.com"

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
            f"""SELECT DISTINCT items."{self.name.url_full_detail}" as url, items.{self.name.low_id_item}
                FROM {self.sql_items_table_raw} as items
                LEFT JOIN (
                    SELECT {self.name.low_id_item}
                    FROM {self.sql_details_table_raw}
                    WHERE "{self.name.seller}"='{self.seller}'
                ) as details
                ON items.{self.name.low_id_item} = details.{self.name.low_id_item}
                WHERE items."{self.name.seller}"='{self.seller}'
                    AND details.{self.name.low_id_item} IS NULL"""
        )
        to_crawl = df_items.to_dict(orient="records")

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
                x = re.findall('url\\("(.+?)"\\)', str(x))[0].replace(  # drouot
                    "size=small", "size=phare"
                )
            else:
                x = str(x).replace("size=small", "size=phare")
                x = x.split("\n")[0].split(" ")[0]  # sothebys

            if x[0] == "/" and "https" not in x:  # millon
                x = self.root_url + x
            return x

        except Exception:
            self._log.error(x)
            return np.nan

    def pre_clean_description(self, row):
        if self.name.detailed_description in row.keys():
            x = row[self.name.detailed_description].split("CONDITIONS DE VENTES")[
                0
            ]  # millon
            return x
        return None

    def crawling_details_function(self, driver, kwargs):

        # crawl detail of one url
        if self.name.low_id_item in kwargs.keys():
            id_item = kwargs[self.name.low_id_item]
        else:
            raise Exception(
                f"Should have passed {self.name.low_id_item} info along url, got {kwargs}"
            )

        # get infos
        try:
            if self.seller == "sothebys":
                infos = self.crawl_iteratively_sothebys_detail(
                    driver=driver, config=self.detailed_infos
                )
            else:
                infos = self.crawl_iteratively(
                    driver=driver, config=self.detailed_infos
                )
        except Exception as e:
            self._log.info(f"Details crawling failed \ {e}")

        # save infos
        if len(infos) == 1:

            row = infos[0]

            list_url_pictures = list(
                set(
                    [
                        self.clean_url_pictures(x)
                        for x in row[self.name.url_picture]
                        if x not in ["", "nan", None, '""'] and len(str(x)) >= 15
                    ]
                )
            )
            list_url_pictures = (
                None if len(list_url_pictures) == 0 else list_url_pictures
            )

            if list_url_pictures:
                list_id_pictures = [encode_file_name(str(x)) for x in list_url_pictures]
            else:
                list_id_pictures = None

            if row[self.name.detailed_description] not in ["", np.nan, None, '""']:
                try:
                    # save new detail infos
                    new_result = Details(
                        id_item=id_item,
                        URL_FULL_DETAILS=row["CURRENT_URL"],
                        DETAIL_TITLE=(
                            row[self.name.detailed_title]
                            if self.name.detailed_title in row.keys()
                            else None
                        ),
                        DETAIL_DESCRIPTION=self.pre_clean_description(row),
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
                        URL_PICTURE=list_url_pictures,
                        ID_PICTURE=list_id_pictures,
                    )

                    self.insert_raw_to_table(
                        unique_id_col=self.name.low_id_item,
                        row_dict=new_result.dict(),
                        table_name=self.sql_details_table_raw,
                    )

                    # save new pictures infos
                    if list_url_pictures:
                        for i, url_picture in enumerate(list_url_pictures):
                            if list_id_pictures[i] not in BLACK_LIST_ID_PICTURE:

                                # TODO : if id_pict already exist & id_item not in the list, append
                                new_picture = Pictures(
                                    id_picture=list_id_pictures[i],
                                    list_id_item=[new_result.id_item],
                                    URL_PICTURE=url_picture,
                                    SELLER=self.seller,
                                    IS_FILE=False,
                                )

                                self.insert_raw_to_table(
                                    unique_id_col=self.name.low_id_picture,
                                    row_dict=new_picture.dict(),
                                    table_name=self.sql_pictures_table_raw,
                                    do_replace=False,
                                )

                except Exception as e:
                    self._log.error(f"Something wrong happened {e}")

        return driver, infos
