from datetime import datetime
import pandas as pd 
import os 
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.utils.utils_crawler import save_picture_crawled

class StepCrawlingPictures(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int,
                 seller : str = "christies"):

        super().__init__(context=context, config=config, threads=threads)

        self.seller = seller
        self.infos_data_path = self._config.crawling[self.seller].save_data_path
        self.save_picture_path = self._config.crawling[self.seller].save_picture_path
        self.today = datetime.today()
        
        self.per_element = self._config.crawling[self.seller].detailed.per_element
    
    # second crawling step  to get list of pieces per auction 
    def get_list_items_to_crawl(self):

        # get clean seller bdd
        df = self.read_sql_data(self.seller + "_202403")
        df = df.loc[df[self.name.id_picture].isnull()]
        liste_urls = df[self.name.url_picture].drop_duplicates().tolist()

        return liste_urls
    
    def crawling_picture(self, driver):

        # crawl detail of one url  
        url = driver.current_url
        picture_id = os.path.basename(url)

        # save pictures & infos
        message = save_picture_crawled(url, self.save_picture_path, picture_id)

        return driver, message