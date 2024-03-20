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

        # https://www.sothebys.com/en/results?from=3%2F1%2F2024&to=3%2F31%2F2024&f0=1709269200000-1711857600000&q=
        #TODO: up to 2007 - 2004 is off

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
        new_liste_lots = self.get_elements(driver, "CLASS_NAME", "SearchModule-results-item")

        while len(liste_lots) != len(new_liste_lots):
            liste_lots = new_liste_lots.copy()
            counter_pages += 1

            self.scrowl_driver(driver, Y=4000)
            time.sleep(3)
            
            new_liste_lots = self.get_elements(driver, "CLASS_NAME", "SearchModule-results-item")

        self._log.info(f"NBR PAGES  IS = {counter_pages}")

        return liste_lots

    def crawling_list_auctions_function(self, driver, config):

        # crawl infos 
        crawl_conf = config.crawling[self.seller]
        auctions_infos_path = crawl_conf.save_data_path_auctions
        query = os.path.basename(driver.current_url.replace("results?", "").replace("%2F", "-"))
        message = ""

        list_infos = []
        liste_lots = self.load_all_page(driver)
        
        # save pict
        for lot in tqdm.tqdm(liste_lots):

            lot_info = {} 

            # get auction link for futur crawling
            try:
                link = self.get_element_infos(lot, "CLASS_NAME", "Card-info-container", "href")
                if link != "":
                    lot_info["URL_AUCTION"] = link
                else:
                    lot_info["URL_AUCTION"] = "MISSING_URL_AUCTION"

                # get infos 
                lot_info["TITLE"] = self.get_element_infos(lot, "CLASS_NAME", "Card-title")
                lot_info["DATE"] = self.get_element_infos(lot, "CLASS_NAME", "Card-details")
                lot_info["TYPE_SALE"] = self.get_element_infos(lot, "CLASS_NAME", "Card-category")
            
                list_infos.append(lot_info)
            
            except Exception as e:
                message = e 

        df_infos = pd.DataFrame().from_dict(list_infos)
        self.save_infos(df_infos, path=auctions_infos_path + f"/{query}.csv")

        return driver, message