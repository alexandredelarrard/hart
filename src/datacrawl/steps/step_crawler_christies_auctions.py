from datetime import datetime
from typing import List
from omegaconf import DictConfig

import pandas as pd 
import tqdm
import time

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.utils.utils_crawler import (get_files_already_done, 
                                    keep_files_to_do)

class StepCrawlingChristiesAuctions(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int):

        super().__init__(context=context, config=config, threads=threads)
        self.seller = "christies"        
        self.auctions_data_path = self._config.crawling[self.seller].save_data_path_auctions
        self.root_url_auctions = self._config.crawling[self.seller].auctions_url
        self.today = datetime.today()

        self.crawler_infos = self._config.crawling[self.seller].auctions

    # first crawling level # list of auctions in the past to get urls 
    def get_auctions_urls_to_wrawl(self) -> List[str]:
        """
        Liste of all auctions on the month over the world done by christies
        keep only the month / year pair not already crawled
        """

        to_crawl = self.urls_to_crawl()
        already_crawled = get_files_already_done(file_path=self.auctions_data_path, 
                                                url_path=self.root_url_auctions)
        liste_urls = keep_files_to_do(to_crawl, already_crawled)
        
        return liste_urls
    
    def urls_to_crawl(self):
        to_crawl = []

        for year in range(1999, self.today.year + 1 ):
            if year == self.today.year:
                range_month = range(1, self.today.month+1)
            else:
                range_month = range(1, 13)

            for month in range_month:
                to_crawl.append(self.root_url_auctions + f"month={month}&year={year}")
        return to_crawl
    
    def handle_signups(self, driver):

        # check signup
        try:
            signup = self.get_elements(driver, "CLASS_NAME", 'fsu--wrapper')
            if len(signup) !=0:
                self.click_element(signup[0], "CLASS_NAME", "closeiframe")
                time.sleep(0.5)

        except Exception:
            pass

    def crawling_list_auctions_function(self, driver):

        # crawl infos 
        query = driver.current_url.replace(self.root_url_auctions, "")
        message = ""

        list_infos = self.crawl_iteratively(driver, self.crawler_infos)

        df_infos = pd.DataFrame().from_dict(list_infos)
        self.save_infos(df_infos, path=self.auctions_data_path + f"/{query}.csv")

        return driver, message
    