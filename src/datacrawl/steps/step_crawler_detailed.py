from omegaconf import DictConfig
import numpy as np
import time

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling
from src.dataclean.transformers.TextCleaner import TextCleaner
from src.utils.utils_crawler import (read_crawled_csvs, 
                                    read_crawled_pickles,
                                    keep_files_to_do,
                                    define_save_paths)

class StepCrawlingDetailed(Crawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int,
                 seller : str = "christies",
                 save_queue_size : int = 500,
                 mode: str= "history",
                 recrawl_pictures: bool = False):

        self.seller = seller
        self.paths = define_save_paths(config, self.seller, mode=mode)
        
        kwargs = {}
        if "crawler_infos" in config.crawling[self.seller].detailed.keys():
            kwargs = config.crawling[self.seller].detailed["crawler_infos"]

        # initialize crawler as queue saving 
        super().__init__(context=context, 
                         config=config, 
                         threads=threads, 
                         save_in_queue=True, 
                         save_queue_size_step=save_queue_size,
                         save_queue_path=self.paths["details"],
                         kwargs=kwargs)
        
        self.sql_table_name = TextCleaner(context=context, config=config).get_sql_db_name(self.seller, mode)
        self.recrawl_pictures = recrawl_pictures
        self.items_col_names= self.name.dict_rename_items()
        self.details_col_names= self.name.dict_rename_detail()
        
        self.detailed_infos = self._config.crawling[self.seller]["detailed"]

    # second crawling step  to get list of pieces per auction 
    def get_list_items_to_crawl(self):

        # get detail urls to crawl
        df = read_crawled_csvs(path=self.paths["infos"])
        df = df.rename(columns=self.items_col_names)
        df = df.sort_values([self.name.url_full_detail, self.name.brut_result],ascending=[0,0])
        to_crawl = df.loc[df[self.name.url_full_detail].notnull(), 
                            self.name.url_full_detail].drop_duplicates().tolist()
        
        # get already crawled urls 
        df_crawled = read_crawled_pickles(path=self.paths["details"])
        df_crawled = df_crawled.rename(columns=self.details_col_names)
        if df_crawled.shape[0] != 0:
            if self.recrawl_pictures:
                df_crawled = self.recrawl_pictures_missing(df_crawled)
            already_crawled = df_crawled[self.name.url_full_detail].drop_duplicates().tolist()
        else:
            already_crawled = []

        liste_urls = keep_files_to_do(to_crawl, already_crawled)
        return liste_urls
    
    def recrawl_pictures_missing(self, df_crawled):
        # remove crawled having url picture missing
        if self.name.url_picture in df_crawled.columns:
            df_crawled[self.name.url_picture] = np.where(df_crawled[self.name.url_picture].apply(lambda x: "data:image/svg+xml;base64," in x),
                                        np.nan, 
                                        df_crawled[self.name.url_picture])
            df_crawled = df_crawled.loc[df_crawled[self.name.url_picture].notnull()]
        else:
            df_crawled = self.read_sql_data(self.sql_table_name)
            df_crawled = df_crawled.loc[df_crawled[self.name.url_picture].notnull()&(df_crawled[self.name.id_picture] != "FAKE_PICTURE")]

        return df_crawled
    
    def crawl_iteratively_sothebys_detail(self, driver, config):
        url = driver.current_url
        infos = []
        if "/en/buy/" in url:
            infos = self.crawl_iteratively(driver, config.buy_url)
        elif "/en/auctions" in url: 
            infos = self.crawl_iteratively(driver, config.auctions_url)
        else:
            self._log.warning(f"Could not crawl url {url} for {self.seller}")
        return infos
    
    def crawling_details_function(self, driver):
        try:
            infos = eval(f"self.crawl_iteratively_{self.seller}_detail(driver=driver, config=self.detailed_infos)")
        except Exception as e:
            self._log.debug(e)
            infos = self.crawl_iteratively(driver=driver, config=self.detailed_infos)
        self._log.debug(infos)
        return driver, infos
        