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

        # TODO: handle pdfs downloading and extraction ... Low prio

    def urls_to_crawl(self, df_auctions) -> List[str]:
        
        # CRAWLING TO DO 
        to_crawl = df_auctions.loc[df_auctions[self.name.url_auction] != "MISSING_URL_AUCTION", 
                                    self.name.url_auction].drop_duplicates().tolist()
        
        return to_crawl

    def check_loggedin(self, driver, counter=0):

        mdp = os.environ[f"{self.seller.upper()}_MDP"]
        email = os.environ[f"{self.seller.upper()}_EMAIL"]

        if "Abonnez-vous" in self.get_element_infos(driver, "TAG_NAME", "header"):
            time.sleep(3)
            self.click_element(driver, "CLASS_NAME", "menuLinkConnection")
            time.sleep(2)

            self.send_keys_element(driver, "ID", "authenticate-email", email)
            time.sleep(2)
            self.send_keys_element(driver, "ID", "password", mdp)
            time.sleep(1)

            self.click_element(driver, "ID", "menuLoginButton0")
            time.sleep(3)

            if "Le Magazine" in self.get_element_infos(driver, "TAG_NAME", "header"):
                return driver
            else:
                if counter < 2:
                    self.check_loggedin(driver, counter+1)
                else: 
                    raise Exception("CANNOT LOG IN TO DROUOT")

        else:
            return driver
        
    def get_page_number(self, driver):
        # get page number
        page_nbr = self.get_element_infos(driver, "CLASS_NAME", "fontRadikalBold")

        if len(page_nbr) != 0:
            page_nbr = int(page_nbr) // 50 + 1
        else:
            page_nbr = 0

        return page_nbr


    def crawl_iteratively_seller(self, driver, config: Dict):

        # log in if necessary
        url = driver.current_url.split("?controller=")[0]

        # crawl infos 
        list_infos = []
        
        driver = self.check_loggedin(driver)
        page_nbr = self.get_page_number(driver)

        for i, new_url in enumerate([url + f"?page={x}" for x in range(1, page_nbr+1)]):
            if i != 1:
                self.get_url(driver, new_url)
                
            new_infos = self.crawl_iteratively(driver, config)
            list_infos = list_infos + new_infos

            # url_picture = re.findall(r'\((.*?)\)', style_tagname_pict)[-1]
            # return eval(str(url_picture))

        return list_infos