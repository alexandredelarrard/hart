from datetime import datetime
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling
from src.datacrawl.utils.utils_drouot_items import DrouotItems
from src.datacrawl.utils.utils_christies_items import ChristiesItems
from src.datacrawl.utils.utils_sothebys_items import SothebysItems
from src.datacrawl.utils.utils_millon_items import MillonItems
from src.utils.utils_crawler import (
    encode_file_name,
)
from src.schemas.crawling_schemas import Auctions, Items


class StepCrawlingItems(Crawling):

    def __init__(
        self,
        context: Context,
        config: DictConfig,
        threads: int,
        seller: str,
    ):

        self.today = datetime.today()
        self.seller = seller.lower()
        self.sql_auction_table_raw = Auctions.__tablename__
        self.sql_items_table_raw = Items.__tablename__

        kwargs = {}
        if "crawler_infos" in config.crawling[self.seller]["items"].keys():
            kwargs = config.crawling[self.seller]["items"]["crawler_infos"]

        super().__init__(
            context=context,
            config=config,
            threads=threads,
            kwargs=kwargs,
        )

        self.root_url = self._config.crawling[self.seller].webpage_url
        self.items_infos = self._config.crawling[self.seller]["items"]

        self.seller_utils = eval(
            f"{self.seller.capitalize()}Items(context=context, config=config)"
        )

    # second crawling step  to get list of pieces per auction
    def get_list_items_to_crawl(self):

        # AUCTIONS
        df_auctions = self.read_sql_data(
            f"""SELECT DISTINCT auction.\"{self.name.url_auction}\"
                FROM {self.sql_auction_table_raw} as auction
                LEFT JOIN (
                    SELECT {self.name.low_id_auction}
                    FROM {self.sql_items_table_raw}
                    WHERE \"{self.name.seller}\"='{self.seller}'
                ) as items
                ON auction.{self.name.low_id_auction} = items.{self.name.low_id_auction}
                WHERE auction.\"{self.name.seller}\"='{self.seller}'
                    AND items.{self.name.low_id_auction} IS NULL"""
        )
        to_crawl = df_auctions[self.name.url_auction].tolist()
        to_crawl = self.seller_utils.urls_to_crawl(to_crawl)

        self._log.info(f"Nbr auction pages To crawl {len(to_crawl)}")

        return to_crawl

    def crawl_items_iteratively(self, driver):

        # crawl infos
        query = encode_file_name(driver.current_url)
        list_infos = self.seller_utils.crawl_iteratively_seller(
            driver, self.items_infos
        )
        for row in list_infos:
            if row[self.name.url_full_detail] and row[self.name.url_full_detail] != "":

                row[self.name.url_auction] = self.clean_url(row["CURRENT_URL"])

                try:
                    new_result = Items(
                        id_item=encode_file_name(row[self.name.url_full_detail]),
                        id_auction=encode_file_name(row[self.name.url_auction]),
                        URL_AUCTION=row[self.name.url_auction],
                        URL_FULL_DETAILS=row[self.name.url_full_detail],
                        AUCTION_DATE=(
                            row[self.name.date]
                            if self.name.date in row.keys()
                            else None
                        ),
                        LOT_NUMBER=(
                            row[self.name.lot] if self.name.lot in row.keys() else None
                        ),
                        ITEM_TITLE=(
                            row[self.name.item_title]
                            if self.name.item_title in row.keys()
                            else None
                        ),
                        ITEM_DESCRIPTION=(
                            row[self.name.item_description]
                            if self.name.item_description in row.keys()
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
                        FILE=query,
                    )
                    self.insert_raw_to_table(
                        unique_id_col=self.name.low_id_item,
                        row_dict=new_result.dict(),
                        table_name=self.sql_items_table_raw,
                    )

                except Exception as e:
                    self._log.error(f"Something wrong happened {e}")

        return driver, list_infos
