
from typing import List
from omegaconf import DictConfig
import pandas as pd 

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling
from src.datacrawl.utils.utils_drouot_auctions import DrouotAuctions
from src.datacrawl.utils.utils_christies_auctions import ChristiesAuctions
from src.datacrawl.utils.utils_sothebys_auctions import SothebysAuctions
from src.datacrawl.utils.utils_millon_auctions import MillonAuctions
from src.utils.utils_crawler import (get_files_done_from_path, 
                                    keep_files_to_do,
                                    save_infos,
                                    define_save_paths,
                                    define_start_date,
                                    define_end_date)

class StepCrawlingAuctions(Crawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int,
                 seller: str,
                 start_date: str = None,
                 end_date: str = None,
                 mode: str= "history"):

        self.seller = seller.lower()
        self.paths = define_save_paths(config, self.seller, mode=mode)

        kwargs = {}
        if "crawler_infos" in config.crawling[self.seller].auctions.keys():
            kwargs = config.crawling[self.seller].auctions["crawler_infos"]

        super().__init__(context=context, config=config, threads=threads, save_queue_path=self.paths["auctions"], kwargs=kwargs)

        self.url_auctions = self._config.crawling[self.seller].auctions_url
        history_start_year = self._config.crawling[self.seller].history_start_year
        self.start_date = define_start_date(start_date, history_start_year)
        self.end_date = define_end_date(end_date)

        self.auctions_infos = self._config.crawling[self.seller]["auctions"]
        self.seller_utils = eval(f"{self.seller.capitalize()}Auctions(context=context, config=config)")

    # first crawling level # list of auctions in the past to get urls 
    def get_auctions_urls_to_crawl(self) -> List[str]:
        """
        Liste of all auctions on the month over the world done by christies
        keep only the month / year pair not already crawled
        """

        to_crawl = self.seller_utils.urls_to_crawl(self.start_date, self.end_date, self.url_auctions)
        already_crawled = get_files_done_from_path(file_path=self.paths["auctions"], 
                                                    url_path=self.url_auctions)
        liste_urls = keep_files_to_do(to_crawl, already_crawled)
        
        return liste_urls

    def crawling_auctions_iteratively(self, driver):

        # crawl infos 
        query = driver.current_url.replace(self.url_auctions, "").replace("results?", "").replace("%2F", "-")
        list_infos = self.seller_utils.crawl_iteratively(driver, self.auctions_infos)

        df_infos = pd.DataFrame().from_dict(list_infos)
        save_infos(df_infos, path=self.paths["auctions"] + f"/{query}.csv")

        return driver, list_infos
    