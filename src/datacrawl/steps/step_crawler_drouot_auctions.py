from typing import List
from omegaconf import DictConfig

import pandas as pd 
import tqdm

from selenium.webdriver.common.by import By

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.utils.utils_crawler import (get_files_already_done, 
                                    keep_files_to_do)

class StepCrawlingDrouotAuctions(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int, 
                 nbr_auction_pages : int = 2566):

        super().__init__(context=context, config=config, threads=threads)

        self.seller = "drouot"     
        self.nbr_auction_pages= nbr_auction_pages # to put 
        self.auctions_data_path = self._config.crawling[self.seller].save_data_path_auctions
        self.root_url_auctions = self._config.crawling[self.seller].auctions_url

        self.liste_elements = self._config.crawling[self.seller].auctions.liste_elements
        self.per_element = self._config.crawling[self.seller].auctions.per_element


    def get_auctions_urls_to_wrawl(self) -> List[str]:

        to_crawl = [self.root_url_auctions + f"page={x}" for x in range(1,self.nbr_auction_pages+1)]
        already_crawled = get_files_already_done(file_path=self.auctions_data_path, 
                                                url_path=self.root_url_auctions)
        liste_urls = keep_files_to_do(to_crawl, already_crawled)
        return liste_urls
    
    def get_url_auctions(self, driver):
        all_hrefs = self.get_elements(driver, "TAG_NAME", "a")
        links = [x.get_attribute("href") for x in all_hrefs]
        links = [x for x in links if x and "modal-content" not in x]
        if len(links) !=0:
            return links[0]
        else:
            return "MISSING_URL_AUCTION"

    def crawling_list_auctions_function(self, driver):

        # crawl infos 
        query = driver.current_url.replace(self.root_url_auctions, "")
        message = ""

        list_infos = []
        liste_lots = self.get_elements(driver, 
                                       self.liste_elements.by_type, 
                                       self.liste_elements.value_css)

        # save pict
        for lot in tqdm.tqdm(liste_lots[1:]):

            lot_info = {} 

            try:
                lot_info[self.name.url_auction] = self.get_url_auctions(lot)
                new_info = self.extract_element_infos(lot, self.per_element)
                lot_info.update(new_info)
                list_infos.append(lot_info)
            
            except Exception as e:
                message = e 

        df_infos = pd.DataFrame().from_dict(list_infos)
        self.save_infos(df_infos, path=self.auctions_data_path + f"/{query}.csv")

        return driver, message