import glob
import urllib
from omegaconf import DictConfig

import pandas as pd 
from selenium.webdriver.common.by import By

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling

class StepCrawlingMet(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int):

        super().__init__(context=context, config=config, threads=threads)
        self.seller = "met"

    def get_urls(self):

        root = self._config.crawling[self.seller].webpage_url
        def find_url(x):
            return root + x.split("\\")[-1].replace("_", "/")

        # get all retrieved images already done 
        list_images = glob.glob(self._config.crawling[self.seller].save_picture_path + "/*.jpg")
        output_list = list(map(find_url, list_images))

        # finalize the url list 
        if self._config.crawling[self.seller]["url_path"] != "":
            df = pd.read_csv(self._config.crawling[self.seller]["url_path"])
            urls = df["Link Resource"].to_list()
            urls = list(set(urls) - set(output_list))[::-1]

            self._log.info(f" DONE : {len(output_list)} TODO : {len(urls)}")
            return urls
        else:
            return []


    def crawling_function(self, driver, config):

        crawl_conf = config.crawling[self.seller]
        image_path = crawl_conf.save_picture_path
        message = ""

        try:
            a = driver.find_element(By.XPATH, "//img[@id='artwork__image']")
            src = a.get_attribute('src')
            
            image_name =driver.current_url.replace(crawl_conf.webpage_url, "").replace("/", "_")
            urllib.request.urlretrieve(src, image_path + f"/{image_name}.jpg")

        except Exception as e: 
            message=e
            return driver, message

        return driver, message

