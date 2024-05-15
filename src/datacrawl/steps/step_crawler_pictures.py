from datetime import datetime
import glob
import os 
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.datacrawl.utils.utils_pictures import PicturesUtils
from src.utils.utils_crawler import (save_picture_crawled,
                                     save_canvas_picture,
                                     keep_files_to_do,
                                     define_save_paths,
                                     read_crawled_pickles,
                                     encode_file_name)

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
        self.paths = define_save_paths(config, self.seller, mode=mode)
        self.crawler_infos = self._config.crawling[self.seller]
        
        self.utils = PicturesUtils(context=context, config=config)
        self.per_element = self._config.crawling[self.seller].detailed.per_element
    
    # second crawling step  to get list of pieces per auction 
    def get_list_items_to_crawl(self, mode=None):

        # extract all picture urls to crawl from details dataframes 
        df_details = read_crawled_pickles(path=self.paths["details"])
        df_details = eval(f"self.utils.get_pictures_url_{self.seller}(df_details, mode)")
        
        # picture id done 
        done = glob.glob(self.paths["pictures"] + "/*.jpg")
        done = [os.path.basename(x).replace(".jpg","") for x in done]

        # KEEP THE ONES TO CRAWL
        liste_ids = keep_files_to_do(df_details[self.name.id_picture].unique(), done)
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
    
    def crawling_canvas(self, driver):

        # crawl detail of one url  
        picture_id = encode_file_name(os.path.basename(driver.current_url))

        if "pictures" not in self.crawler_infos.keys():
            raise Exception("Need to provide crawling infos on picture when using mode canvas")

        # save pictures & infos
        list_infos = self.seller_utils.crawl_iteratively(driver, self.crawler_infos["pictures"])
        message = save_canvas_picture(list_infos["URL_PICTURE_CANVAS"], self.paths["pictures"], picture_id)

        return driver, message
