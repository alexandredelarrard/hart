from omegaconf import DictConfig
import re
import time
import os 
from typing import Dict

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling

class SothebysItems(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config, threads=1)
        self.mdp = os.environ["SOTHEBYS_MDP"]
        self.email = os.environ["SOTHEBYS_EMAIL"]

        self.root_url = self._config.crawling["sothebys"].webpage_url
        self.to_replace=("?lotFilter=AllLots","")
        self.to_split=["?p=", 0]
        
        # TODO: include the F1 webpage formating from sothebys # weird webpage format regarding F1
        # TODO: refacto check logged in and click page and cookies
        # weird formating: https://www.sothebys.com/en/buy/auction/2021/a-brilliant-menagerie
    
    def urls_to_crawl(self, df_auctions):
        to_crawl = (df_auctions.loc[(self.name.url_auction != "MISSING_URL_AUCTION")&
                            (df_auctions[self.name.url_auction].notnull()), 
                            self.name.url_auction]
                            .drop_duplicates()
                            .tolist())
        to_crawl = [x for x in to_crawl if "/en/auctions" in x or "/en/buy/" in x] # no F1 and catalogue urls
        return to_crawl
 
    def check_loggedin(self, driver, counter=0):
        driver_log = self.get_element_infos(driver, "CLASS_NAME", "AuctionsModule-auction-info-total")
        if driver_log == "":
            driver_log = self.get_element_infos(driver, "CLASS_NAME", "PageHeader-hat")
        
        if "my account" in driver_log.lower():
            return driver

        if 'log in' in driver_log.lower():
            self.click_element(driver, "CLASS_NAME", "SothebysHat-aemLogin")
            time.sleep(1)

            self.send_keys_element(driver, "ID", "email", self.email)
            time.sleep(1)
            self.send_keys_element(driver, "ID", "password", self.mdp)
            time.sleep(1)

            self.click_element(driver, "ID", "login-button-id")
            time.sleep(2)

            if counter < 3:
                driver = self.check_loggedin(driver, counter+1)
                return driver
            else: 
                self._log.warning("CANNOT LOG IN TO SOTHEBYS")
                return driver

        else:
            self._log.debug("LOGGED IN TO SOTHEBYS")
            return driver
        
    def accept_cookies(self, driver, counter=0):
        cookie = self.get_element_infos(driver, "ID", "onetrust-button-group-parent")
        if "Reject All" in cookie: 
            self.click_element(driver, "ID", "onetrust-reject-all-handler")
            time.sleep(1)

            if counter < 2:
                    driver = self.accept_cookies(driver, counter+1)
                    return driver
            else: 
                raise Exception("CANNOT CLICK COOKIES")
        else:
            return driver
        
    def click_page(self, driver, position):

        navigation = self.get_elements(driver, "XPATH", "//nav[@aria-label='pagination navigation']/ul/li")

        infos = {}
        for i, element in enumerate(navigation): 
            if element.text != "":
                infos[i] = element.text
        reversed = {v: k for k, v in infos.items()}

        if position <= 1:
            return driver 
        else:
            if str(position) in reversed.keys():
                navigation[reversed[str(position)]].click()
                time.sleep(3)
                return driver
            else: 
                self._log.warning(f"PAGE NUMBER {position} NOT AVILABLE IN PAGINATION {reversed}")
                return driver

    def crawl_auction_pages(self, driver, config, url):
        list_infos = []
        pages = self.get_page_number(driver, "CLASS_NAME", "AuctionsModule-lotsCount", divider=12)

        for new_url in [url + f"?p={x}" for x in range(1, max(1, pages)+1)]:
            self.get_url(driver, new_url)
            new_infos = self.crawl_iteratively(driver, config.auctions_url)
            list_infos = list_infos + new_infos
        return list_infos
    
    def crawl_buy_pages(self, driver, config, url):
        list_infos = []
        self.get_url(driver, url)
        pages = self.get_page_number(driver, "CLASS_NAME", "css-1xtedx2", divider=48)
 
        for position in range(1, max(1, pages)+1):
            self.click_page(driver, position)
            new_infos = self.crawl_iteratively(driver, config.buy_url)
            list_infos = list_infos + new_infos
        return list_infos

    def crawl_iteratively_seller(self, driver, config: Dict):

        list_infos = []

        # crawl infos 
        url = driver.current_url

        # check if pages exists : 
        error = self.get_element_infos(driver, "CLASS_NAME", "ErrorPage-body")

        if error == "":
            driver = self.accept_cookies(driver)
            driver = self.check_loggedin(driver)
            if "/en/auctions/" in url:
                list_infos = self.crawl_auction_pages(driver, config, url)
            elif "/en/buy/auction" in url:
                list_infos = self.crawl_buy_pages(driver, config, url)
            else:
                self._log.warning(f"TYPE OF URL NOT HANDLED {url}")
        else:
            self._log.warning(f"PAGE {url} DOES NOT EXIST {error}")

        return list_infos