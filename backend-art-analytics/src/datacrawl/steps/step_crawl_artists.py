from datetime import datetime
import string
import pandas as pd
import os
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling
from src.utils.utils_crawler import save_infos


class StepCrawlingArtists(Crawling):

    def __init__(self, context: Context, config: DictConfig, threads: int):

        super().__init__(
            context=context,
            config=config,
            threads=threads,
            save_in_queue=False,
            text_only=False,
        )

        self.root_url = self._config.side_crawling.artist_db.webpage_url
        self.infos_data_path = self._config.side_crawling.artist_db.save_data_path
        self.today = datetime.today()

        self.pages_infos = self._config.side_crawling.artist_db.pages
        self.crawler_infos = self._config.side_crawling.artist_db.artist_names

    # second crawling step  to get list of pieces per auction
    def get_list_items_to_crawl(self):
        liste_urls = []
        for letter in list(string.ascii_lowercase):
            liste_urls.append(self.root_url + letter.upper())
        return liste_urls

    def get_pages_per_letter(self, driver):
        nbr_lots = self.crawl_iteratively(driver, self.pages_infos)
        return nbr_lots

    def crawling_artists(self, driver):

        # crawl detail of one url
        url = driver.current_url
        file_id = os.path.basename(url)

        list_infos = []
        iterative_pages = self.get_pages_per_letter(driver)
        for i, new_url in enumerate(iterative_pages):
            self._log.info(f"CRAWLING URL : {new_url}")
            if i != 1:
                self.get_url(driver, new_url["URLS"])

            new_infos = self.crawl_iteratively(driver, self.crawler_infos)
            list_infos = list_infos + new_infos

        df_infos = pd.DataFrame().from_dict(list_infos)
        save_infos(df_infos, path=self.infos_data_path + f"/{file_id}.csv")

        return driver, list_infos
