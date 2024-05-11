from omegaconf import DictConfig
import re
import time
from typing import Dict

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling

class SothebysItems(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config, threads=1)
        self.root_url = self._config.crawling["sothebys"].webpage_url
        self.to_replace=(self.root_url, '')

        # weird webpage format regarding F1
        # TODO: include the F1 webpage formating from sothebys*
        # TODO : pages with /en/buy
        # TODO: re extract pictures with src = data:image/svg+xml;base64 = 50%
    
    def urls_to_crawl(self, df_auctions):
        to_crawl = (df_auctions.loc[(self.name.url_auction != "MISSING_URL_AUCTION")&
                            (df_auctions[self.name.url_auction].notnull()), 
                            self.name.url_auction]
                            .drop_duplicates()
                            .tolist())
        to_crawl = [x for x in to_crawl if "rmsothebys" not in x and "/en/buy/" not in x]
        return to_crawl
    
    def get_number_pages_auctions(self, driver):
        
        nbr_lots =self.get_element_infos(driver, "CLASS_NAME", "AuctionsModule-lotsCount")
        if nbr_lots != "":
            nbr_lots = re.findall("(\\d+)", nbr_lots)[0]
            return int(nbr_lots) // 12 + 1
        else:
            return 2

    def get_number_pages_buy(self, driver):
     
        next_button_status = self.get_element_infos(driver, "XPATH", 
                                                    "//button[@aria-label='Go to next page.']", 
                                                    "aria-disabled")
        if next_button_status != "":
            return next_button_status
        else:
            "true"

    def crawl_iteratively(self, driver, config: Dict):

        # crawl infos 
        url = driver.current_url
        list_infos = []

        # check if pages exists : 
        error = self.get_element_infos(driver, "CLASS_NAME", "ErrorPage-body")

        if error == "":
            if "www.sothebys.com" in url:
                if "/en/auctions/" in url:
                    
                    pages = self.get_number_pages_auctions(driver)
                    for i, new_url in enumerate([url + f"?p={x}" for x in range(1, pages+1)]):
                        if i != 1:
                            self.get_url(driver, new_url)
                        new_infos = self.crawl_iteratively(driver, config.auctions_url)
                        list_infos = list_infos + new_infos

                if "/en/buy/" in url:
                    next_button_call = "false"
                    page_counter = 0
                    
                    while next_button_call != "true":
                        page_counter +=1
                        new_infos = self.crawl_iteratively(driver, config.buy_url)
                        list_infos = list_infos + new_infos
                        time.sleep(1)

                        next_button_call = self.get_number_pages_buy(driver)
                        self.click_element(driver, "XPATH", "//button[@aria-label='Go to next page.']")
                        time.sleep(4)

                    self._log.info(f"CRAWLED nbr pages = {page_counter}")
                    
            else:
                self._log.error(f"TYPE OF URL NOT HANDLED {driver.current_url}")
        
        else:
            self._log.warning(f"PAGE {url} DOES NOT EXIST {error}")

        return list_infos