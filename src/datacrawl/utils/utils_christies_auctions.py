
from omegaconf import DictConfig
import time

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling


class ChristiesAuctions(Crawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)
        self.history_start_year = self._config.crawling["christies"].history_start_year

    def urls_to_crawl(self, start_date, end_date, url_auctions):
        to_crawl = []
        start_year = max(start_date.year, self.history_start_year)

        for year in range(start_year, end_date.year + 1):
            if year == end_date.year:
                end_month = end_date.month+1 # current month even if no results 
                start_month = 1
            else:
                end_month=13
                start_month=1
            
            if year == start_year:
                start_month = start_date.month

            for month in range(start_month, end_month):
                to_crawl.append(url_auctions + f"month={month}&year={year}")
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
