from datetime import datetime
from pathlib import Path
from omegaconf import DictConfig
import pandas as pd

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling
from src.datacrawl.utils.utils_drouot_items import DrouotItems
from src.datacrawl.utils.utils_christies_items import ChristiesItems
from src.datacrawl.utils.utils_sothebys_items import SothebysItems
from src.datacrawl.utils.utils_millon_items import MillonItems
from src.utils.utils_crawler import (
    read_crawled_csvs,
    get_files_already_done,
    keep_files_to_do,
    encode_file_name,
    save_infos,
    define_save_paths,
)


class StepCrawlingItems(Crawling):

    def __init__(
        self,
        context: Context,
        config: DictConfig,
        threads: int,
        seller: str,
        mode: str = "history",
    ):

        self.today = datetime.today()
        self.seller = seller.lower()
        self.paths = define_save_paths(config, self.seller, mode=mode)

        kwargs = {}
        if "crawler_infos" in config.crawling[self.seller]["items"].keys():
            kwargs = config.crawling[self.seller]["items"]["crawler_infos"]

        super().__init__(
            context=context,
            config=config,
            threads=threads,
            save_queue_path=self.paths["infos"],
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
        df_auctions = read_crawled_csvs(path=self.paths["auctions"])
        to_crawl = self.seller_utils.urls_to_crawl(df_auctions)

        # ITEMS crawled
        df_infos = read_crawled_csvs(path=self.paths["infos"])
        already_crawled = get_files_already_done(
            df=df_infos,
            to_replace=self.seller_utils.to_replace,
            split=self.seller_utils.to_split,
        )

        # TO CRAWL
        liste_urls = keep_files_to_do(to_crawl, already_crawled)

        return liste_urls

    def crawl_items_iteratively(self, driver):

        # crawl infos
        query = encode_file_name(driver.current_url)
        list_infos = self.seller_utils.crawl_iteratively_seller(
            driver, self.items_infos
        )

        df_infos = pd.DataFrame().from_dict(list_infos)
        save_infos(df_infos, path=self.paths["infos"] / Path(f"{query}.csv"))

        return driver, list_infos
