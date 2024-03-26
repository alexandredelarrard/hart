from datetime import datetime
import os 
from omegaconf import DictConfig
import pandas as pd 
import tqdm
import pickle
import time

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.utils.utils_crawler import (read_crawled_csvs, 
                                    get_files_already_done, 
                                    keep_files_to_do,
                                    encode_file_name)

class StepCrawlingChristiesItems(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int):

        super().__init__(context=context, config=config, threads=threads)
        
        self.seller = "christies"        
        self.infos_data_path = self._config.crawling[self.seller].save_data_path
        self.auctions_data_path = self._config.crawling[self.seller].save_data_path_auctions
        self.root_url = self._config.crawling[self.seller].webpage_url
        self.correction_urls_auction = self._config.crawling[self.seller].correction_urls_auction
        self.today = datetime.today()

        self.crawler_infos = self._config.crawling[self.seller].items

        # TODO: recrawl SSO urls redirected because only first page was 
        # crawled because missing ?loadall=true after rediction
    
    # second crawling step  to get list of pieces per auction 
    def get_list_items_to_crawl(self):

        full_display = "/?loadall=true"

        df = read_crawled_csvs(path=self.auctions_data_path)
        to_crawl = df.loc[df[self.name.url_auction] != "MISSING_URL_AUCTION", 
                             self.name.url_auction].drop_duplicates().tolist()
        to_crawl = [x[:-1] if x[-1] == "/" else x for x in to_crawl]

        df_infos = read_crawled_csvs(path=self.infos_data_path)
        already_crawled = get_files_already_done(df=df_infos, 
                                                url_path=self.root_url,
                                                to_replace=('&page=2&sortby=lotnumber',''))
        liste_urls = keep_files_to_do(to_crawl, already_crawled)
        
        return [x + full_display for x in liste_urls]
    
    def create_mapping_dynamic_auction_url(self, driver, df_auctions):

        mapping_dynamic_urls = {}
        sso = df_auctions[self.name.url_auction].apply(lambda x : "sso?" in x)
        df_auctions = df_auctions[sso]

        for url in tqdm.tqdm(df_auctions[self.name.url_auction].tolist()):
            driver.get(url)
            time.sleep(0.4)
            mapping_dynamic_urls[url] = driver.current_url
        
        with open(self.correction_urls_auction, "wb") as f:
            pickle.dump(mapping_dynamic_urls, f)
    
    def handle_signups(self, driver):

        # check signup
        try:
            signup = self.get_elements(driver, "CLASS_NAME", 'fsu--wrapper')
            if len(signup) !=0:
                self.click_element(signup[0], "CLASS_NAME", "closeiframe")
                time.sleep(0.5)

        except Exception:
            pass
    
    def crawling_list_items_function(self, driver):

        # crawl infos 
        query = encode_file_name(os.path.basename(driver.current_url.replace("/?loadall=true","")))
        list_infos = self.crawl_iteratively(driver, self.crawler_infos)

        df_infos = pd.DataFrame().from_dict(list_infos)
        self.save_infos(df_infos, path=self.infos_data_path + f"/{query}.csv")

        return driver, list_infos
