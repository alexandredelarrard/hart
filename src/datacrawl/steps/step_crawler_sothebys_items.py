from datetime import datetime
import os 
from omegaconf import DictConfig

import pandas as pd 
import re
import time

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.utils.utils_crawler import (read_crawled_csvs, 
                                    get_files_already_done, 
                                    keep_files_to_do,
                                    encode_file_name)

class StepCrawlingSothebysItems(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int):

        super().__init__(context=context, config=config, threads=threads)

        self.seller = "sothebys"        
        self.infos_data_path = self._config.crawling[self.seller].save_data_path
        self.auctions_data_path = self._config.crawling[self.seller].save_data_path_auctions
        self.root_url = self._config.crawling[self.seller].webpage_url
        self.url_crawled = self._config.crawling[self.seller].url_crawled
        self.today = datetime.today()

        self.crawler_infos_auction_url = self._config.crawling[self.seller].items.auctions_url
        self.crawler_infos_buy_url = self._config.crawling[self.seller].items.buy_url

        # weird webpage format regarding F1
        # TODO: include the F1 webpage formating from sothebys*
        # TODO : pages with /en/buy
        # TODO: re extract pictures with src = data:image/svg+xml;base64 = 50%
    
    def get_list_items_to_crawl(self):

        df = read_crawled_csvs(path=self.auctions_data_path)
        to_crawl = (
                    df.loc[(self.name.url_auction != "MISSING_URL_AUCTION")&
                            (df[self.name.url_auction].notnull()), 
                            self.name.url_auction]
                            .drop_duplicates()
                            .tolist()
                    )
        to_crawl = [x for x in to_crawl if "rmsothebys" not in x and "/en/buy/" not in x]

        # ALREADY DONE
        df_infos = read_crawled_csvs(path=self.infos_data_path)
        already_crawled = get_files_already_done(df=df_infos, 
                                                url_path='')
        liste_urls = keep_files_to_do(to_crawl, already_crawled)

        return liste_urls
    
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

    def crawling_list_items_function(self, driver):

        # crawl infos 
        query = encode_file_name(os.path.basename(driver.current_url))
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
                        new_infos = self.crawl_iteratively(driver, self.crawler_infos_auction_url)
                        list_infos = list_infos + new_infos

                if "/en/buy/" in url:
                    next_button_call = "false"
                    page_counter = 0
                    
                    while next_button_call != "true":
                        page_counter +=1
                        new_infos = self.crawl_iteratively(driver, self.crawler_infos_buy_url)
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

        df_infos = pd.DataFrame().from_dict(list_infos)
        self.save_infos(df_infos, path=self.infos_data_path + f"/{query}.csv")

        return driver, list_infos