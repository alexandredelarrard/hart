from typing import Dict
import pandas as pd 
import time
import os

from omegaconf import DictConfig
from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling

class SothebysAuctions(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config, threads=1)
        self.history_start_year = self._config.crawling["sothebies"].history_start_year

    def urls_to_crawl(self, start_date, end_date, url_auctions):

        start_year = max(start_date.year, self.history_start_year)
        to_crawl = []
        step = 2505600000
        start = 1709269200000 # for 1 march 2024

        for year in range(end_date.year, start_year - 1, -1):

            if year == end_date.year:
                end_month = end_date.month # current month even if no results 
                start_month = 0
            else:
                end_month=12
                start_month=0
            
            if year == start_year:
                start_month = start_date.month

            for month in range(end_month, start_month, -1):
                to_crawl.append(url_auctions + f"from={month}%2F{1}%2F{year}&to={month}%2F{31}%2F{year}&f0={start}-{start+step}&q=")
                start = start - step # decrease starting point 

        return to_crawl
    
    def load_all_page(self, driver, config : Dict):

        liste_lots = []
        counter_pages = 0
        new_liste_lots = self.get_elements(driver, 
                                       config.liste_elements.by_type, 
                                       config.liste_elements.value_css)

        while len(liste_lots) != len(new_liste_lots):
            liste_lots = new_liste_lots.copy()
            counter_pages += 1

            self.scrowl_driver(driver, Y=4000)
            time.sleep(2.5)
            
            new_liste_lots = self.get_elements(driver, 
                                       config.liste_elements.by_type, 
                                       config.liste_elements.value_css)

        self._log.info(f"NBR PAGES  IS = {counter_pages}")

    def crawl_iteratively(self, driver, config : Dict):
        self.load_all_page(driver, config)
        list_infos = self.crawl_iteratively(driver, config)
        return list_infos