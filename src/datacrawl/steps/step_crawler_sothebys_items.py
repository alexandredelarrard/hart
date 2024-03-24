from datetime import datetime
import os 
from omegaconf import DictConfig

import pandas as pd 
import tqdm
import re
import time
import hashlib

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.utils.utils_crawler import (read_crawled_csvs, 
                                    get_files_already_done, 
                                    keep_files_to_do,
                                    save_picture_crawled,
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
        self.save_picture_path = self._config.crawling[self.seller].save_picture_path
        self.today = datetime.today()

        self.liste_elements = self._config.crawling[self.seller].items.liste_elements
        self.per_element = self._config.crawling[self.seller].items.per_element
        
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

        already_crawled = get_files_already_done(file_path=self.infos_data_path, 
                                                    url_path='')
        liste_urls = keep_files_to_do(to_crawl, already_crawled)

        return liste_urls
    
    def get_sothebys_url_infos(self, driver, image_path):

        list_infos = []
        message = ""

        liste_lots = self.get_elements(driver, "XPATH", "//div[@aria-label='List of lots']/div/div") 
        if len(liste_lots) == 0:
            liste_lots = self.get_elements(driver, "CLASS_NAME", "AuctionsModule-results-item")

        # save pict
        for lot in tqdm.tqdm(liste_lots):
            lot_info = {} 
        
            lot_info[self.name.date] = self.get_element_infos(driver, "CLASS_NAME", "css-1bnt3nz")
            if lot_info[self.name.date] == "":
                lot_info[self.name.date] = self.get_element_infos(driver, "CLASS_NAME", "AuctionsModule-auction-info")

            # URL for DETAIL                
            lot_info[self.name.full_detail] = self.get_element_infos(lot, "CLASS_NAME", "css-1ivophs", type="href")
            if lot_info[self.name.full_detail] == "":
                lot_info[self.name.full_detail] = self.get_element_infos(lot, "XPATH", 
                                                                            "//div[@class='image']/a", type="href")

            # TITLE
            lot_info[self.name.item_infos] = lot.text
            lot_info[self.name.item_title] = lot_info[self.name.item_infos].split("\n")[0]
            if lot_info[self.name.item_infos] == "":
                lot_info[self.name.item_title] = self.get_element_infos(lot, "CLASS_NAME", "title")
                lot_info[self.name.item_infos] = self.get_element_infos(lot, "CLASS_NAME", "description")

            lot_info[self.name.brut_result] = self.get_element_infos(lot, "TAG_NAME", "span")
            if lot_info[self.name.brut_result] == "":
                lot_info[self.name.brut_result] = self.get_element_infos(lot, "CLASS_NAME", "estimate")

            # PICTURE 
            lot_info[self.name.url_picture] = self.get_element_infos(lot, "TAG_NAME", "img", type="src").replace("extra_small", "small")
            lot_info[self.name.id_picture] = encode_file_name(os.path.basename(lot_info[self.name.url_picture]))

            # save pictures & infos
            save_picture_crawled(lot_info[self.name.url_picture], image_path, lot_info[self.name.id_picture])
            time.sleep(0.1)
            
            list_infos.append(lot_info)
            
        return message, list_infos
    
    
    def get_number_pages(self, driver, type_url = "auctions"):
        
        if type_url == "auctions":
            nbr_lots =self.get_element_infos(driver, "CLASS_NAME", "AuctionsModule-lotsCount")
            if nbr_lots != "":
                nbr_lots = re.findall("(\\d+)", nbr_lots)[0]
                return int(nbr_lots) // 12 + 1
        
        if type_url == "buy": 
            next_button_status = self.get_element_infos(driver, "XPATH", "//button[@aria-label='Go to next page.']", "aria-disabled")
            if next_button_status != "":
                return next_button_status
            else:
                "true"

    def crawling_list_items_function(self, driver):

        # crawl infos 
        query = encode_file_name(os.path.basename(driver.current_url))
        url = driver.current_url
        
        message = ""
        list_infos = []

        # check if pages exists : 
        error = self.get_element_infos(driver, "CLASS_NAME", "ErrorPage-body")

        if error == "":
            if "www.sothebys.com" in url:
                if "/en/auctions/" in url:
                    
                    pages = self.get_number_pages(driver, type_url="auctions")
                    message, new_infos = self.get_sothebys_url_infos(driver, image_path=self.save_picture_path)
                    list_infos = list_infos + new_infos

                    for new_url in [url + f"?p={x}" for x in range(2, pages+1)]:
                        self.get_url(driver, new_url)
                        message, new_infos = self.get_sothebys_url_infos(driver, image_path=self.save_picture_path)
                        list_infos = list_infos + new_infos

                if "/en/buy/" in url:
                    next_button_call = "false"
                    page_counter = 0
                    
                    while next_button_call != "true":
                        page_counter +=1
                        message, new_infos = self.get_sothebys_url_infos(driver, image_path=self.save_picture_path)
                        list_infos = list_infos + new_infos
                        time.sleep(1)

                        next_button_call = self.get_number_pages(driver, type_url="buy")
                        self.click_element(driver, "XPATH", "//button[@aria-label='Go to next page.']")
                        time.sleep(4)

                    self._log.info(f"CRAWLED nbr pages = {page_counter}")
                    
            else:
                self._log.error(f"TYPE OF URL NOT HANDLED {driver.current_url}")
        
        else:
            self._log.warning(f"PAGE {url} DOES NOT EXIST {error}")

        df_infos = pd.DataFrame().from_dict(list_infos)
        self.save_infos(df_infos, path=self.infos_data_path + f"/{query}.csv")

        return driver, message