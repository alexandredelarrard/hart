from typing import List
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling
from src.datacrawl.utils.utils_drouot_auctions import DrouotAuctions
from src.datacrawl.utils.utils_christies_auctions import ChristiesAuctions
from src.datacrawl.utils.utils_sothebys_auctions import SothebysAuctions
from src.datacrawl.utils.utils_millon_auctions import MillonAuctions
from src.utils.utils_crawler import (
    define_save_paths,
    define_start_date,
    define_end_date,
    encode_file_name,
)
from src.schemas.crawling_schemas import Auctions


class StepCrawlingAuctions(Crawling):

    def __init__(
        self,
        context: Context,
        config: DictConfig,
        threads: int,
        seller: str,
        start_date: str = None,
        end_date: str = None,
    ):

        self.seller = seller.lower()
        self.sql_auction_table_raw = Auctions.__tablename__

        kwargs = {}
        if "crawler_infos" in config.crawling[self.seller].auctions.keys():
            kwargs = config.crawling[self.seller].auctions["crawler_infos"]

        super().__init__(
            context=context,
            config=config,
            threads=threads,
            kwargs=kwargs,
        )

        self.url_auctions = self._config.crawling[self.seller].auctions_url
        history_start_year = self._config.crawling[self.seller].history_start_year
        self.start_date = define_start_date(start_date, history_start_year)
        self.end_date = define_end_date(end_date)

        self.auctions_infos = self._config.crawling[self.seller].auctions
        self.seller_utils = eval(
            f"{self.seller.capitalize()}Auctions(context=context, config=config)"
        )

    # first crawling level # list of auctions in the past to get urls
    def get_auctions_urls_to_crawl(self) -> List[str]:
        """
        Liste of all auctions on the month over the world done by christies
        keep only the month / year pair not already crawled
        """

        already_crawled = self.read_sql_data(
            f"""SELECT DISTINCT \"{self.name.url_crawled}\"
                FROM {self.sql_auction_table_raw}
                WHERE \"{self.name.seller}\"='{self.seller}' """
        )
        already_crawled = already_crawled[self.name.url_crawled].tolist()

        to_crawl = self.seller_utils.urls_to_crawl(
            self.start_date, self.end_date, self.url_auctions, already_crawled
        )

        return to_crawl

    def crawling_auctions_iteratively(self, driver):

        # crawl infos
        query = (
            driver.current_url.replace(self.url_auctions, "")
            .replace("results?", "")
            .replace("%2F", "-")
        )
        list_infos = self.seller_utils.crawl_iteratively(driver, self.auctions_infos)

        for row in list_infos:
            if row["URL_AUCTION"] and row["URL_AUCTION"] not in [
                "",
                "MISSING_URL_AUCTION",
            ]:
                try:
                    # replace url by true url if sso
                    row["URL_AUCTION"] = self.get_real_url_from_sso(
                        row["URL_AUCTION"], driver
                    )

                    new_result = Auctions(
                        id_auction=encode_file_name(self.clean_url(row["URL_AUCTION"])),
                        URL_AUCTION=row["URL_AUCTION"],
                        AUCTION_TITLE=row["AUCTION_TITLE"],
                        AUCTION_DATE=row["AUCTION_DATE"],
                        SELLER=self.seller,
                        TYPE_SALE=(
                            row["TYPE_SALE"] if "TYPE_SALE" in row.keys() else None
                        ),
                        LOCALISATION=(
                            row["LOCALISATION"]
                            if "LOCALISATION" in row.keys()
                            else None
                        ),
                        HOUSE=row["HOUSE"] if "HOUSE" in row.keys() else self.seller,
                        URL_CRAWLED=row["CURRENT_URL"],
                        FILE=query,
                    )
                    self.insert_raw_to_table(
                        unique_id_col=self.name.low_id_auction,
                        row_dict=new_result.dict(),
                        table_name=self.sql_auction_table_raw,
                    )

                except Exception as e:
                    self._log.error(f"Something wrong happened {e}")

        return driver, list_infos
