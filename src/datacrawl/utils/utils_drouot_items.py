import os
import time
from typing import List, Dict
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling

class DrouotItems(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config, threads=1)
        self.to_replace=()
        self.mdp = os.environ["DROUOT_MDP"]
        self.email = os.environ["DROUOT_EMAIL"]

        # TODO: handle pdfs downloading and extraction ... Low prio

    def urls_to_crawl(self, df_auctions) -> List[str]:
        
        # CRAWLING TO DO 
        to_crawl = df_auctions.loc[df_auctions[self.name.url_auction] != "MISSING_URL_AUCTION", 
                                    self.name.url_auction].drop_duplicates().tolist()
        
        return to_crawl

    def check_loggedin(self, driver, counter=0):

        header = self.get_element_infos(driver, "TAG_NAME", "header")
        if "Mon profil" not in header:
            self.click_element(driver, "XPATH", "//div[@class='floatRight alignRight noPaddingRight']/div[2]")
            time.sleep(1)

            self.send_keys_element(driver, "ID", "authenticate-email", self.email)
            time.sleep(1)
            self.send_keys_element(driver, "ID", "password", self.mdp)
            time.sleep(1)

            self.click_element(driver, "ID", "menuLoginButton0")
            time.sleep(2)

            if counter < 2:
                driver = self.check_loggedin(driver, counter+1)
                return driver
            else: 
                raise Exception("CANNOT LOG IN TO DROUOT")

        else:
            self._log.debug("LOGGED IN TO DROUOT")
            return driver
        
    def get_page_number(self, driver):
        # get page number
        page_nbr = self.get_element_infos(driver, "CLASS_NAME", "fontRadikalBold")

        if len(page_nbr) != 0:
            page_nbr = (int(page_nbr) // 50) + 1
        else:
            page_nbr = 0

        self._log.debug(f"{page_nbr} to crawl")
        return page_nbr


    def crawl_iteratively_seller(self, driver, config: Dict):

        # log in if necessary
        url = driver.current_url.split("?controller=")[0]
        
        driver = self.check_loggedin(driver)
        page_nbr = self.get_page_number(driver)

        # crawl infos 
        list_infos = []
        for new_url in [url + f"?page={x}" for x in range(1, page_nbr + 1)]:
            
            self.get_url(driver, new_url)
            time.sleep(0.3)
                
            new_infos = self.crawl_iteratively(driver, config)
            list_infos = list_infos + new_infos

        return list_infos