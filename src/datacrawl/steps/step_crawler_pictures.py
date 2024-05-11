from datetime import datetime
import pandas as pd 
import glob
import os 
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.utils.utils_crawler import (save_picture_crawled,
                                     keep_files_to_do)

class StepCrawlingPictures(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int,
                 seller : str = "christies"):

        super().__init__(context=context, config=config, threads=threads, save_in_queue=False, text_only=False)

        self.seller = seller
        self.today = datetime.today()
        self.define_save_paths(self.seller) # independant from mode 
        
        self.per_element = self._config.crawling[self.seller].detailed.per_element
    
    # second crawling step  to get list of pieces per auction 
    def get_list_items_to_crawl(self):

        # get clean seller bdd
        df = self.read_sql_data(f"SELECT DISTINCT \"URL_PICTURE\" FROM \"{self.seller.upper() + "_202403"}\" WHERE \"URL_PICTURE\" IS NOT NULL")   
        df[self.name.id_picture] = df[self.name.url_picture].apply(lambda x: os.path.basename(x))

        done = glob.glob(self.pictures_data_path + "/*.jpg")
        done = [os.path.basename(x).replace(".jpg","") for x in done]

        liste_ids = keep_files_to_do(df[self.name.id_picture].tolist(), done)
        df = df.loc[df[self.name.id_picture].isin(liste_ids)].drop_duplicates(self.name.id_picture)
        liste_urls = df[self.name.url_picture].tolist()
        self._log.info(f"NUMBER PICTURES TO CRAWL = {len(liste_urls)}")

        return liste_urls
    
    def crawling_picture(self, driver):

        # crawl detail of one url  
        url = driver.current_url
        picture_id = os.path.basename(url)

        # save pictures & infos
        message = save_picture_crawled(url, self.pictures_data_path, picture_id)

        return driver, message