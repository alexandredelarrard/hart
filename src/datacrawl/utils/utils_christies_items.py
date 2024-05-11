from datetime import datetime
import os 
from omegaconf import DictConfig
import pandas as pd 
import numpy as np
import tqdm
import pickle
import time

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling

class ChristiesItems(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config, threads=1)
        self.correction_urls_auction = self._config.crawling["christies"].correction_urls_auction
        self.to_replace = ('&page=2&sortby=lotnumber','/?loadall=true')
        
        # TODO: recrawl SSO urls redirected because only first page was 
        # crawled because missing ?loadall=true after rediction
    
    # second crawling step  to get list of pieces per auction 
    def urls_to_crawl(self, df_auctions):

        full_display = "/?loadall=true"

        # AUCTIONS
        mapping_urls = self.create_mapping_dynamic_auction_url(df_auctions)
        df_auctions[self.name.url_auction] = np.where(df_auctions[self.name.url_auction].apply(lambda x : "sso?" in x),
                               df_auctions[self.name.url_auction].map(mapping_urls),
                               df_auctions[self.name.url_auction])
        
        to_crawl = df_auctions.loc[df_auctions[self.name.url_auction] != "MISSING_URL_AUCTION", 
                                    self.name.url_auction].drop_duplicates().tolist()
        
        to_crawl = [x[:-1] if x[-1] == "/" else x for x in to_crawl]

        return [x + full_display for x in to_crawl]
    
    def create_mapping_dynamic_auction_url(self, df_auctions):

        driver = self.initialize_driver_chrome()

        # create mapping dict
        mapping_dynamic_urls = {}
        sso = df_auctions[self.name.url_auction].apply(lambda x : "sso?" in x)
        sub_auctions = df_auctions[sso]

        for url in tqdm.tqdm(sub_auctions[self.name.url_auction].tolist()):
            driver.get(url)
            time.sleep(0.4)
            mapping_dynamic_urls[url] = driver.current_url
        
        with open(self.correction_urls_auction, "wb") as f:
            pickle.dump(mapping_dynamic_urls, f)

        driver.close()

        return mapping_dynamic_urls
    
    def handle_signups(self, driver):

        # check signup
        try:
            signup = self.get_elements(driver, "CLASS_NAME", 'fsu--wrapper')
            if len(signup) !=0:
                self.click_element(signup[0], "CLASS_NAME", "closeiframe")
                time.sleep(0.5)

        except Exception:
            pass