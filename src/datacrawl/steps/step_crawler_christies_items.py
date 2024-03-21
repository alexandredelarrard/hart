from datetime import datetime
import os 
from omegaconf import DictConfig

import pandas as pd 
import tqdm
import time

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.utils.utils_crawler import (read_crawled_csvs, 
                                    get_files_already_done, 
                                    keep_files_to_do,
                                    save_picture_crawled,
                                    encode_file_name
                                    )

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
        self.save_picture_path = self._config.crawling[self.seller].save_picture_path
        self.today = datetime.today()
    
    # second crawling step  to get list of pieces per auction 
    def get_list_items_to_crawl(self):

        full_display = "/?loadall=true"

        df = read_crawled_csvs(path=self.auctions_data_path)
        to_crawl = df["URL_AUCTION"].tolist()
        to_crawl = [x[:-1] if x[-1] == "/" else x for x in to_crawl]
        already_crawled = get_files_already_done(file_path=self.infos_data_path, 
                                                      url_path=self.root_url,
                                                      to_replace=('&page=2&sortby=lotnumber',''))
        liste_urls = keep_files_to_do(to_crawl, already_crawled)
        
        return [x + full_display for x in liste_urls]
    
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
        message = ""

        list_infos = []
        liste_lots = self.get_elements(driver, "CLASS_NAME", 'chr-browse-lot-tile-wrapper') 

        # save pict
        for lot in tqdm.tqdm(liste_lots):

            lot_info = {} 
            self.scrowl_driver(driver, Y=150)
            self.handle_signups(driver)
            
            try:
                # URL for DETAIL                
                lot_info["URL_FULL_DETAILS"] = self.get_element_infos(lot, "CLASS_NAME", "chr-lot-tile__link", type="href")
                lot_info["LOT"] = self.get_element_infos(lot, "CLASS_NAME", "chr-lot-tile__content-header")

                # TITLE
                lot_info["INFOS"] = self.get_element_infos(lot, "CLASS_NAME", "chr-lot-tile__content")
                lot_info["SALE"] = self.get_element_infos(lot, "CLASS_NAME", "chr-lot-tile__price-value")
                lot_info["RESULT"] = self.get_element_infos(lot, "CLASS_NAME", "chr-lot-tile__dynamic-price")
                
                # PICTURE 
                lot_info["URL_PICTURE"] = self.get_element_infos(lot, "TAG_NAME", "img", type="src").split("?")[0]
                lot_info["PICTURE_ID"] = encode_file_name(os.path.basename(lot_info["URL_PICTURE"]))

                # save pictures & infos
                save_picture_crawled(lot_info["URL_PICTURE"], self.save_picture_path, lot_info["PICTURE_ID"])
                
                list_infos.append(lot_info)
            
            except Exception as e:
                message = e 

        df_infos = pd.DataFrame().from_dict(list_infos)
        self.save_infos(df_infos, path=self.infos_data_path + f"/{query}.csv")

        return driver, message
