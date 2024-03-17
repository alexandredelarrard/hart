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
                                    keep_files_to_do)

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

    def get_urls(self) -> List[str]:
        
        full_display = "?loadall=true"

        df = read_crawled_csvs(path=self.auctions_data_path)
        to_crawl = df["URL_AUCTION"].tolist()
        already_crawled = get_files_already_done(file_path=self.infos_data_path, 
                                                      url_path=self.root_url)
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
        try:
            page_nbr = re.search('&page=([0-9]*)', driver.current_url).group(1)
        except Exception:
            page_nbr = driver.current_url.split("page=")[1]

        return page_nbr
    
    def get_picture_url(self, lot, driver, counter=0):
        
        try:
            time.sleep(0.15)
            style_tagname_pict = self.get_element_infos(lot, "CLASS_NAME", "imgLot", "style")
            url_picture = re.findall(r'\((.*?)\)', style_tagname_pict)[-1].replace("\"", "")
            picture_id = url_picture.split("path=")[1].replace("/", "_")
            
            return picture_id, url_picture
        
        except Exception as e:
            if counter <3:
                driver.execute_script("window.scrollTo(0, window.scrollY + 120);")
                time.sleep(0.3)
                self.get_picture_url(lot, driver, counter+1)
            else:
                raise Exception(e)
        
        return "", ""


    def crawling_function(self, driver, config):

        # log in if necessary
        driver = self.check_loggedin(driver)
        page_nbr = self.get_page_number(driver)

        # crawl infos 
        crawl_conf = config.crawling[self.seller]
        image_path = crawl_conf.save_picture_path
        infos_path = crawl_conf.save_data_path
        message = ""

        list_infos = []
        time.sleep(1)
        
        liste_lots = self.get_elements(driver, "CLASS_NAME", "Lot")

        # save pict
        for lot in tqdm.tqdm(liste_lots):

            self.scrowl_driver(driver, Y=200)
            time.sleep(0.1)
            lot_info = {} 
            
            try:
                # infos vente
                lot_info["INFOS"] = self.get_element_infos(lot, "CLASS_NAME", "descriptionLot")
                lot_info["NUMBER_LOT"] = lot_info["INFOS"].split("\n")[0].replace("Lot n° ", "")
                lot_info["SALE"] = self.get_element_infos(lot, "CLASS_NAME",  "infoVenteLot")
                lot_info["URL_FULL_DETAILS"] = self.get_element_infos(lot, "TAG_NAME", "a", type="href")
                lot_info["PICTURE_ID"], lot_info["URL_PICTURE"] = self.get_picture_url(lot, driver)

                # save pictures & infos
                save_picture_crawled(lot_info["URL_PICTURE"], image_path, lot_info["PICTURE_ID"])

                list_infos.append(lot_info)
            
            except Exception as e:
                message = e 

        df_infos = pd.DataFrame().from_dict(list_infos)
        self.save_infos(df_infos, path=infos_path + f"/{self.object}_page_{page_nbr}.csv")
        time.sleep(2)
        
        return driver, message
