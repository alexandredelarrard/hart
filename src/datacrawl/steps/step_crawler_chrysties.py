from datetime import datetime
import glob
from typing import List
from omegaconf import DictConfig

import pandas as pd 
import tqdm
import time

from selenium.webdriver.common.by import By

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling

class StepCrawlingChristies(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int):

        super().__init__(context=context, config=config, threads=threads)
        self.seller = "christies"        
        self.root_url_auctions = self._config.crawling[self.seller].webpage_url
        self.today = datetime.today()

    # first crawling level # list of auctions in the past to get urls 
    def get_auctions_urls_to_wrawl(self) -> List[str]:
        """
        Liste of all auctions on the month over the world done by christies
        keep only the month / year pair not already crawled
        """

        liste_urls = []

        for year in range(1999, self.today.year + 1 ):
            if year == self.today.year:
                range_month = range(1,self.today.month+1)
            else:
                range_month = range(1,13)

            for month in range_month:
                liste_urls.append(self.root_url_auctions + f"&month={month}&year={year}")
        
        files_already_done = glob.glob(self._config.crawling[self.seller].save_data_path + "/*.csv")
        files_already_done = [self.root_url_auctions + x.split("/")[-1].replace(".csv","") 
                                                for x in files_already_done]

        liste_urls = list(set(liste_urls) - set(files_already_done))
        self._log.info(f"ALREADY CRAWLED {len(files_already_done)} REMAINING {len(liste_urls)}")

        return liste_urls
    

    def crawling_list_auctions_function(self, driver, config):

        # crawl infos 
        crawl_conf = config.crawling[self.seller]
        infos_path = crawl_conf.save_data_path
        query = driver.current_url.replace(crawl_conf.auctions_url, "")
        message = ""

        list_infos = []
        time.sleep(1)
        
        liste_lots = driver.find_elements(By.XPATH, '//ul[@aria-labelledby="calendar-tab-undefined"]/li')

        # save pict
        for i, lot in tqdm.tqdm(enumerate(liste_lots)):

            lot_info = {} 
            driver.execute_script("window.scrollTo(0, window.scrollY + 150);")
            time.sleep(0.3)
            
            try:
                # URL for DETAIL                
                lot_info["URL_AUCTION"] = lot.find_element(By.CLASS_NAME, 
                                                           "chr-event-tile__title").get_attribute("href")

                # TITLE
                lot_info["TITLE"] = lot.find_element(By.CLASS_NAME, 
                                                    "chr-event-tile__title").text
                # AUCTION LOC
                lot_info["LOCALISATION"] = lot.find_element(By.CLASS_NAME, 
                                                           "chr-label-s").text

                list_infos.append(lot_info)
            
            except Exception as e:
                message = e 

        df_infos = pd.DataFrame().from_dict(list_infos, orient="records")
        self.save_infos(df_infos, path=infos_path + f"/{query}.csv")

        return driver, message

