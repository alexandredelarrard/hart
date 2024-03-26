from typing import List
from omegaconf import DictConfig
from datetime import datetime

import pandas as pd 
import tqdm
import re
import time
import os

from selenium.webdriver.common.by import By

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.utils.utils_crawler import (get_files_already_done, 
                                    keep_files_to_do)

class StepCrawlingSothebysAuctions(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int):

        super().__init__(context=context, config=config, threads=threads)

        self.seller = "sothebys"     
        self.auctions_data_path = self._config.crawling[self.seller].save_data_path_auctions
        self.root_url_auctions = self._config.crawling[self.seller].auctions_url
        self.oldest_year = self._config.crawling[self.seller].oldest_year
        self.today = datetime.today()

        self.crawler_infos = self._config.crawling[self.seller].auctions


    def get_auctions_urls_to_wrawl(self) -> List[str]:
        to_crawl = self.urls_to_crawl()
        already_crawled = get_files_already_done(file_path=self.auctions_data_path, 
                                                url_path=self.root_url_auctions,
                                                to_replace=("-", "%2F"))
        liste_urls = keep_files_to_do(to_crawl, already_crawled)
        return liste_urls
    
    def urls_to_crawl(self):
        to_crawl = []
        step = 2505600000
        start = 1709269200000 # for 1 march 2024

        for year in range(self.today.year, self.oldest_year - 1, -1):
            if year == self.today.year:
                range_month = range(self.today.month, 1-1, -1)
            else:
                range_month = range(12, 0, -1)

            for month in range_month:
                to_crawl.append(self.root_url_auctions + f"from={month}%2F{1}%2F{year}&to={month}%2F{31}%2F{year}&f0={start}-{start+step}&q=")
                start = start - step # decrease starting point 

        return to_crawl
    
    def load_all_page(self, driver):

        liste_lots = []
        counter_pages = 0
        new_liste_lots = self.get_elements(driver, 
                                       self.liste_elements.by_type, 
                                       self.liste_elements.value_css)

        while len(liste_lots) != len(new_liste_lots):
            liste_lots = new_liste_lots.copy()
            counter_pages += 1

            self.scrowl_driver(driver, Y=4000)
            time.sleep(3)
            
            new_liste_lots = self.get_elements(driver, 
                                       self.liste_elements.by_type, 
                                       self.liste_elements.value_css)

        self._log.info(f"NBR PAGES  IS = {counter_pages}")


    def crawling_list_auctions_function(self, driver):

        # crawl infos 
        query = os.path.basename(driver.current_url.replace("results?", "").replace("%2F", "-"))

        self.load_all_page(driver)
        list_infos = self.crawl_iteratively(driver, self.crawler_infos)

        df_infos = pd.DataFrame().from_dict(list_infos)
        self.save_infos(df_infos, path=self.auctions_data_path + f"/{query}.csv")

        return driver, list_infos