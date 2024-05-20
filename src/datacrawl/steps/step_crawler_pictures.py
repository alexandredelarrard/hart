from datetime import datetime
import glob
import os 
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling
from src.dataclean.utils.utils_clean_sothebys import CleanSothebys
from src.dataclean.utils.utils_clean_christies import CleanChristies
from src.dataclean.utils.utils_clean_drouot import CleanDrouot
from src.dataclean.utils.utils_clean_millon import CleanMillon
from src.utils.utils_crawler import (save_picture_crawled,
                                     save_canvas_picture,
                                     keep_files_to_do,
                                     define_save_paths,
                                     read_crawled_pickles)

class StepCrawlingPictures(Crawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int,
                 seller : str = "christies",
                 mode: str = "history"):

        kwargs = {"is_picture": False,
                  "is_javascript": False,
                  "is_cookie" : False}
        # if "crawler_infos" in config.crawling[self.seller].pictures.keys():
            # kwargs = config.crawling[self.seller].pictures["crawler_infos"]

        super().__init__(context=context, config=config, threads=threads, save_in_queue=False, kwargs=kwargs)

        self.seller = seller
        self.today = datetime.today()
        self.paths = define_save_paths(config, self.seller, mode=mode)
        self._infos = self._config.crawling[self.seller]
        
        self.utils = eval(f"Clean{self.seller.capitalize()}(context=context, config=config)")
    
    # second crawling step  to get list of pieces per auction 
    def get_list_items_to_crawl(self, mode=None):

        # extract all picture urls to crawl from details dataframes 
        df_details = read_crawled_pickles(path=self.paths["details"])
        df_details = eval(f"self.utils.get_pictures_url_{self.seller}(df_details, mode)")
        df_details = df_details.loc[(df_details[self.name.url_picture].notnull())&(~df_details[self.name.url_picture].isin(["","nan"]))]
        
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
        picture_id = eval(f"self.utils.naming_picture_{self.seller}(url)")

        # save pictures & infos
        message = save_picture_crawled(url, self.paths["pictures"], picture_id)

        return driver, message
    
    def crawling_canvas(self, driver):

        # crawl detail of one url  
        picture_id = eval(f"self.utils.naming_picture_{self.seller}(url)")

        if "pictures" not in self._infos.keys():
            raise Exception("Need to provide crawling infos on picture when using mode canvas")

        # save pictures & infos
        list_infos = self.seller_utils.crawl_iteratively(driver, self._infos["pictures"])
        message = save_canvas_picture(list_infos["URL_PICTURE_CANVAS"], self.paths["pictures"], picture_id)

        return driver, message
