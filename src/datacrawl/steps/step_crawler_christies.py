from datetime import datetime
import urllib
import os 
from typing import List
from omegaconf import DictConfig

import pandas as pd 
import tqdm
import time

from selenium.webdriver.common.by import By

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.utils.utils_crawler import (read_crawled_csvs, 
                                    get_files_already_done, 
                                    keep_files_to_do)

class StepCrawlingChristies(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int):

        super().__init__(context=context, config=config, threads=threads)
        self.seller = "christies"        
        self.auctions_data_path = self._config.crawling[self.seller].save_data_path_auctions
        self.infos_data_path = self._config.crawling[self.seller].save_data_path
        self.root_url = self._config.crawling[self.seller].webpage_url
        self.root_url_auctions = self._config.crawling[self.seller].auctions_url
        self.today = datetime.today()

    # first crawling level # list of auctions in the past to get urls 
    def get_auctions_urls_to_wrawl(self) -> List[str]:
        """
        Liste of all auctions on the month over the world done by christies
        keep only the month / year pair not already crawled
        """

        to_crawl = []

        for year in range(1999, self.today.year + 1 ):
            if year == self.today.year:
                range_month = range(1, self.today.month+1)
            else:
                range_month = range(1, 13)

            for month in range_month:
                to_crawl.append(self.root_url_auctions + f"month={month}&year={year}")

        already_crawled = get_files_already_done(file_path=self.auctions_data_path, 
                                                url_path=self.root_url_auctions)
        liste_urls = keep_files_to_do(to_crawl, already_crawled)
        
        return liste_urls
    
    def handle_signups(self, driver):

        time.sleep(0.25)

        # check signup
        try:
            signup = driver.find_elements(By.CLASS_NAME, 'fsu--wrapper')
            if len(signup) !=0:
                signup[0].find_element(By.CLASS_NAME, 'closeiframe').click()
                time.sleep(1)
        except Exception:
            pass

    def crawling_list_auctions_function(self, driver, config):

        # crawl infos 
        crawl_conf = config.crawling[self.seller]
        auctions_infos_path = crawl_conf.save_data_path_auctions
        query = driver.current_url.replace(crawl_conf.auctions_url, "")
        message = ""

        list_infos = []
        liste_lots = driver.find_elements(By.XPATH, '//ul[@aria-labelledby="calendar-tab-undefined"]/li')

        # save pict
        for i, lot in tqdm.tqdm(enumerate(liste_lots)):

            lot_info = {} 
            driver.execute_script("window.scrollTo(0, window.scrollY + 150);")
            self.handle_signups(driver)
            
            try:
                # URL for DETAIL                
                lot_info["URL_AUCTION"] = lot.find_element(By.CLASS_NAME, 
                                                           "chr-event-tile__title").get_attribute("href")

                # TITLE
                try:
                    lot_info["TITLE"] = lot.find_element(By.CLASS_NAME, 
                                                    "chr-event-tile__title").text
                except Exception:
                    lot_info["TITLE"] = ""
                
                # AUCTION LOC
                try:
                    lot_info["LOCALISATION"] = lot.find_element(By.CLASS_NAME, 
                                                            "chr-label-s").text
                except Exception:
                    lot_info["LOCALISATION"] = ""

                list_infos.append(lot_info)
            
            except Exception as e:
                message = e 

        df_infos = pd.DataFrame().from_dict(list_infos)
        self.save_infos(df_infos, path=auctions_infos_path + f"/{query}.csv")

        return driver, message
    
    # second crawling step  to get list of pieces per auction 
    def get_list_items_to_crawl(self):

        full_display = "?loadall=true"

        df = read_crawled_csvs(path=self.auctions_data_path)
        to_crawl = df["URL_AUCTION"].tolist()
        already_crawled = get_files_already_done(file_path=self.infos_data_path, 
                                                      url_path=self.root_url)
        liste_urls = keep_files_to_do(to_crawl, already_crawled)
        
        return [x + full_display for x in liste_urls]
    
    def crawling_list_items_function(self, driver, config):

        # crawl infos 
        crawl_conf = config.crawling[self.seller]
        infos_path = crawl_conf.save_data_path
        query = os.path.basename(driver.current_url.replace("/?loadall=true",""))
        image_path = crawl_conf.save_picture_path
        message = ""

        list_infos = []
        liste_lots = driver.find_elements(By.CLASS_NAME, 'chr-browse-lot-tile-wrapper')

        # save pict
        for i, lot in tqdm.tqdm(enumerate(liste_lots)):

            lot_info = {} 
            driver.execute_script("window.scrollTo(0, window.scrollY + 150);")
            self.handle_signups(driver)
            
            try:
                # URL for DETAIL                
                lot_info["URL_FULL_DETAILS"] = lot.find_element(By.CLASS_NAME, 
                                                    "chr-lot-tile__link").get_attribute("href")
                
                lot_info["LOT"] = lot.find_element(By.CLASS_NAME, "chr-lot-tile__content-header").text

                # TITLE
                try:
                    lot_info["INFOS"] = lot.find_element(By.CLASS_NAME, 
                                                    "chr-lot-tile__content").text
                except Exception:
                    lot_info["INFOS"] = ""

                lot_info["SALE"] = lot.find_element(By.CLASS_NAME, 
                                                    "chr-lot-tile__price-value").text
                lot_info["RESULT"] = lot.find_element(By.CLASS_NAME, 
                                                    "chr-lot-tile__dynamic-price").text
                
                # PICTURE 
                try:
                    lot_info["URL_PICTURE"] = lot.find_element(By.TAG_NAME, 'img').get_attribute("src").split("?")[0]
                    lot_info["PICTURE_ID"] = os.path.basename(lot_info["URL_PICTURE"])

                    # save pictures & infos
                    if not os.path.isfile(image_path + f"/{lot_info["PICTURE_ID"]}.jpg"):
                        if "https" in lot_info["URL_PICTURE"]:
                            urllib.request.urlretrieve(lot_info["URL_PICTURE"], image_path + f"/{lot_info["PICTURE_ID"]}.jpg")
                
                except Exception:
                    lot_info["URL_PICTURE"] = ""
                    lot_info["PICTURE_ID"] = "MISSING.jpg"
                
                list_infos.append(lot_info)
            
            except Exception as e:
                message = e 

        df_infos = pd.DataFrame().from_dict(list_infos)
        self.save_infos(df_infos, path=infos_path + f"/{query}.csv")

        return driver, message
    
    



    


