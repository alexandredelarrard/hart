import os
import re
from typing import List
from omegaconf import DictConfig

import pandas as pd 
import tqdm
import time

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.utils.utils_crawler import (read_crawled_csvs,
                                     save_picture_crawled,
                                     get_files_already_done,
                                    keep_files_to_do,
                                    encode_file_name)

class StepCrawlingDrouotItems(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int, 
                 object : str = ""):

        super().__init__(context=context, config=config, threads=threads)

        self.seller = "drouot"     
        self.object = object   
        self.infos_data_path = self._config.crawling[self.seller].save_data_path
        self.auctions_data_path = self._config.crawling[self.seller].save_data_path_auctions
        self.root_url = self._config.crawling[self.seller].webpage_url
        self.save_picture_path = self._config.crawling[self.seller].save_picture_path
        self.url_crawled = self._config.crawling[self.seller].url_crawled

        self.liste_elements = self._config.crawling[self.seller].items.liste_elements
        self.per_element = self._config.crawling[self.seller].items.per_element

        # TODO: handle pdfs downloading and extraction ... Low prio
        # TODO : missing 1M pictures /3.3M items

    def get_urls(self) -> List[str]:
        
        full_display = ""

        df = read_crawled_csvs(path=self.auctions_data_path)
        to_crawl = df.loc[df[self.name.url_auction] != "MISSING_URL_AUCTION", 
                             self.name.url_auction].drop_duplicates().tolist()
        already_crawled = get_files_already_done(file_path=self.infos_data_path, 
                                                url_path=self.url_crawled)
        liste_urls = keep_files_to_do(to_crawl, already_crawled)
        
        return [x + full_display for x in liste_urls]

    def check_loggedin(self, driver, counter=0):

        mdp = os.environ[f"{self.seller.upper()}_MDP"]
        email = os.environ[f"{self.seller.upper()}_EMAIL"]

        if "Abonnez-vous" in self.get_element_infos(driver, "TAG_NAME", "header"):
            time.sleep(3)
            self.click_element(driver, "CLASS_NAME", "menuLinkConnection")
            time.sleep(2)

            self.send_keys_element(driver, "ID", "authenticate-email", email)
            time.sleep(2)
            self.send_keys_element(driver, "ID", "password", mdp)
            time.sleep(1)

            self.click_element(driver, "ID", "menuLoginButton0")
            time.sleep(3)

            if "Le Magazine" in self.get_element_infos(driver, "TAG_NAME", "header"):
                return driver
            else:
                if counter < 2:
                    self.check_loggedin(driver, counter+1)
                else: 
                    raise Exception("CANNOT LOG IN TO DROUOT")

        else:
            return driver
        
    def get_page_number(self, driver):
        # get page number
        page_nbr = self.get_element_infos(driver, "CLASS_NAME", "fontRadikalBold")

        if len(page_nbr) != 0:
            page_nbr = int(page_nbr) // 50 + 1
        else:
            page_nbr = 0

        return page_nbr
    
    def get_picture_url(self, lot, driver, counter=0):
        
        try:
            style_tagname_pict = self.get_value_of_css_element(lot, "CLASS_NAME", 
                                                               "imgLot", 
                                                               "background-image")
            url_picture = re.findall(r'\((.*?)\)', style_tagname_pict)[-1]
            return eval(str(url_picture))
        
        except Exception as e:
            if counter < 3:
                self.scrowl_driver(driver, 120)
                time.sleep(0.3)
                self.get_picture_url(lot, driver, counter+1)
            else:
                raise Exception(e)
        
        return ""
    
    def crawl_info_per_page(self, driver, list_infos):

        liste_lots = self.get_elements(driver, 
                                       self.liste_elements.by_type, 
                                       self.liste_elements.value_css)
        time.sleep(0.35)
        message = ""

        # save pict
        for lot in tqdm.tqdm(liste_lots):

            self.scrowl_driver(driver, Y=200)
            lot_info = {} 
            
            try:
                # infos vente
                new_info = self.extract_element_infos(lot, self.per_element)
                lot_info.update(new_info)
               
                lot_info[self.name.url_picture] = self.get_picture_url(lot, driver)
                lot_info[self.name.id_picture] = encode_file_name(os.path.basename(lot_info[self.name.url_picture]))
                
                # save pictures & infos
                save_picture_crawled(lot_info[self.name.url_picture], 
                                     self.save_picture_path, 
                                     lot_info[self.name.id_picture])
                list_infos.append(lot_info)
            
            except Exception as e:
                message = e 

        return message, list_infos


    def crawling_function(self, driver):

        # log in if necessary
        driver = self.check_loggedin(driver)
        page_nbr = self.get_page_number(driver)
        url = driver.current_url.split("?controller=")[0]
        query = encode_file_name(os.path.basename(url))

        # crawl infos 
        list_infos = []
        message, list_infos = self.crawl_info_per_page(driver, list_infos)

        if page_nbr >= 2:
            for new_url in [url + f"?page={x}" for x in range(2, page_nbr+1)]:
                self.get_url(driver, new_url)
                message, list_infos = self.crawl_info_per_page(driver, list_infos)

        df_infos = pd.DataFrame().from_dict(list_infos)
        self.save_infos(df_infos, path=self.infos_data_path + f"/{query}.csv")
        
        return driver, message
