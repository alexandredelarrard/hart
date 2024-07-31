import os
import time
from typing import List, Dict
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling


class DrouotItems(Crawling):

    def __init__(self, context: Context, config: DictConfig):

        super().__init__(context=context, config=config)
        self.to_replace = ()
        self.to_split = ["?page", 0]
        self.mdp = os.environ["DROUOT_MDP"]
        self.email = os.environ["DROUOT_EMAIL"]

        # TODO: handle pdfs downloading and extraction ... Low prio

    def check_loggedin(self, driver, counter=0):

        if "/catalogue/resultats/" in driver.current_url:
            return driver

        header = self.get_element_infos(driver, "TAG_NAME", "header")
        if "Mon profil" not in header:
            self.click_element(
                driver,
                "XPATH",
                "//div[@class='floatRight alignRight noPaddingRight']/div[2]",
            )
            time.sleep(1)

            self.send_keys_element(driver, "ID", "authenticate-email", self.email)
            time.sleep(1)
            self.send_keys_element(driver, "ID", "password", self.mdp)
            time.sleep(1)

            self.click_element(driver, "ID", "menuLoginButton0")
            time.sleep(2)

            if counter < 2:
                driver = self.check_loggedin(driver, counter + 1)
                return driver
            else:
                raise Exception("CANNOT LOG IN TO DROUOT")

        else:
            self._log.debug("LOGGED IN TO DROUOT")
            return driver

    def crawl_iteratively_seller(self, driver, config: Dict):

        # log in if necessary
        url = driver.current_url.split("?controller=")[0]

        driver = self.check_loggedin(driver)
        page_nbr = self.get_page_number(
            driver, "CLASS_NAME", "fontRadikalBold", divider=50
        )

        # crawl infos
        list_infos = []
        for new_url in [url + f"?page={x}" for x in range(1, max(page_nbr, 1) + 1)]:
            self.get_url(driver, new_url)
            new_infos = self.crawl_iteratively(driver, config)
            list_infos = list_infos + new_infos
        return list_infos
