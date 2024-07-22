import glob
import urllib
from omegaconf import DictConfig

import pandas as pd
from selenium.webdriver.common.by import By

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling


class StepCrawlingMet(Crawling):

    def __init__(self, context: Context, config: DictConfig, threads: int):

        super().__init__(context=context, config=config, threads=threads)
        self.seller = "met"
        self.root_path = self._context.paths["ROOT"]
        self.picture_path = (
            self.root_path + self._config.crawling[self.seller].save_picture_path
        )

    def get_urls(self):

        root = self._config.crawling[self.seller].webpage_url

        def find_url(x):
            return root + x.split("\\")[-1].replace("_", "/")

        # get all retrieved images already done
        list_images = glob.glob(self.picture_path + "/*.jpg")
        output_list = list(map(find_url, list_images))

        # finalize the url list
        if self._config.crawling[self.seller].url_path != "":
            df = pd.read_csv(
                self.root_path + self._config.crawling[self.seller].url_path
            )
            urls = df["Link Resource"].to_list()
            urls = list(set(urls) - set(output_list))[::-1]

            self._log.info(f" DONE : {len(output_list)} TODO : {len(urls)}")
            return urls
        else:
            return []

    def crawling_function(self, driver):

        message = ""

        try:
            a = driver.find_element(By.XPATH, "//img[@id='artwork__image']")
            src = a.get_attribute("src")

            image_name = driver.current_url.replace(
                self._config.crawling[self.seller].webpage_url, ""
            ).replace("/", "_")
            urllib.request.urlretrieve(src, self.picture_path + f"/{image_name}.jpg")

        except Exception as e:
            message = e
            return driver, message

        return driver, message
