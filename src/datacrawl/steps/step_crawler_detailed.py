from datetime import datetime
import os 
from omegaconf import DictConfig

import pandas as pd 
import tqdm
import time
import pickle
import hashlib

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.utils.utils_crawler import (read_crawled_csvs, 
                                    read_crawled_pickles,
                                    keep_files_to_do)

class StepCrawlingDetailed(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int,
                 seller : str = "christies"):

        super().__init__(context=context, config=config, threads=threads, text_only=True)

        self.seller = seller
        self.infos_data_path = self._config.crawling[self.seller].save_data_path
        self.details_data_path = self._config.crawling[self.seller].save_data_path_details
        self.today = datetime.today()
        self.queries = self._config.crawling[self.seller].detailed.queries
    
    # second crawling step  to get list of pieces per auction 
    def get_list_items_to_crawl(self):

        df = read_crawled_csvs(path=self.infos_data_path)
        to_crawl = df.loc[df["URL_FULL_DETAILS"].notnull(), 
                            "URL_FULL_DETAILS"].drop_duplicates().tolist()
        df_crawled = read_crawled_pickles(path=self.details_data_path)

        if df_crawled.shape[0] != 0:
            already_crawled = df_crawled["URL"].tolist()
        else:
            already_crawled = []
            
        liste_urls = keep_files_to_do(to_crawl, already_crawled)
        return liste_urls
    
    def crawling_details_function(self, driver, config):

        # crawl detail of one url  
        url = driver.current_url
        try:
            query = hashlib.sha256(str.encode(os.path.basename(url))).hexdigest()
        except Exception:
            query = url.replace(self.root_url, "")
        message = ""

        infos = {"URL" : url}
        for step, step_values in self.queries.items(): 
            infos[step] =  self.get_element_infos(driver, 
                                    step_values["by_type"], 
                                    step_values["value_css"])
        
        self.save_infos(infos, path=self.details_data_path + f"/{query}.pickle")

        return driver, message
