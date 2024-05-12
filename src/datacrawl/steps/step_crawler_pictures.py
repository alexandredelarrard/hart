from datetime import datetime
import pandas as pd 
import glob
import os 
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.utils.utils_crawler import (save_picture_crawled,
                                     keep_files_to_do,
                                     define_save_paths,
                                     read_crawled_csvs,
                                     read_crawled_pickles)

class StepCrawlingPictures(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int,
                 seller : str = "christies",
                 mode: str = "history"):

        super().__init__(context=context, config=config, threads=threads, save_in_queue=False, text_only=False)

        self.seller = seller
        self.today = datetime.today()
        self.paths = define_save_paths(config, self.seller, mode=mode) # independant from mode 
        
        self.per_element = self._config.crawling[self.seller].detailed.per_element
    
    # second crawling step  to get list of pieces per auction 
    def get_list_items_to_crawl(self):

        # extract all picture urls to crawl from details dataframes 
        df_details = read_crawled_pickles(path=self.paths["details"])
        df_details = df_details.explode(self.name.url_picture)
        df_details = df_details.loc[df_details[self.name.url_picture].notnull()]
        df_details[self.name.url_picture] = df_details[self.name.url_picture].apply(lambda x: 
                                                str(x).split("url(")[-1].split(")")[0].replace("\"", "").replace("size=small", "size=phare"))
        df_details[self.name.id_picture] = df_details[self.name.url_picture].apply(lambda x: os.path.basename(x))
        df_details = df_details.loc[df_details[self.name.url_picture] != "nan"]
         
        # picture id done 
        done = glob.glob(self.paths["pictures"] + "/*.jpg")
        done = [os.path.basename(x).replace(".jpg","") for x in done]

        # KEEP THE ONES TO CRAWL
        liste_ids = keep_files_to_do(df_details[self.name.id_picture].tolist(), done)
        df_details = df_details.loc[df_details[self.name.id_picture].isin(liste_ids)].drop_duplicates(self.name.id_picture)
        liste_urls = df_details[self.name.url_picture].tolist()
        self._log.info(f"NUMBER PICTURES TO CRAWL = {len(liste_urls)}")

        return liste_urls
    
    def crawling_picture(self, driver):

        # crawl detail of one url  
        url = driver.current_url
        picture_id = os.path.basename(url)

        # save pictures & infos
        message = save_picture_crawled(url, self.paths["pictures"], picture_id)

        return driver, message