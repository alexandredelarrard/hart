from typing import Dict
import pandas as pd 
import time
from datetime import timedelta

from src.constants.variables import date_format
from omegaconf import DictConfig
from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling

class SothebysAuctions(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config, threads=1)
        self.history_start_year = self._config.crawling["sothebys"].history_start_year
        self.ref = {"date": pd.to_datetime("2006-01-01", format=date_format), "value": 1136156400000, "step_size": 86400000}

    def get_url_ref(self, date):
        nbr_days = (date - self.ref["date"]).days 
        return self.ref["value"] + nbr_days*self.ref["step_size"]

    def urls_to_crawl(self, start_date, end_date, url_auctions):

        start_year = max(start_date.year, self.history_start_year)
        to_crawl = []

        for year in range(start_year, end_date.year +1):

            if year == end_date.year:
                end_month = end_date.month 
                start_month = 1
            else:
                end_month=13
                start_month=1
            
            if year == start_year:
                start_month = start_date.month

            for month in range(start_month, end_month):
                start_date_range = pd.to_datetime(f"{year}-{month}-01", format=date_format)
                end_date_range = start_date_range + timedelta(days=31)
                lower_ref = self.get_url_ref(start_date_range)
                higher_ref = self.get_url_ref(end_date_range)
                start_date_range = end_date_range.strftime("%m-%d-%Y").replace("-", "%2F")
                end_date_range = end_date_range.strftime("%m-%d-%Y").replace("-", "%2F")
                to_crawl.append(url_auctions + f"from={end_date_range}&to={start_date_range}&f0={lower_ref}-{higher_ref}&q=")

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