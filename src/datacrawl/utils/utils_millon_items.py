from typing import List
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling

class MillonItems(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config, threads=1)
        self.to_replace=()

    def urls_to_crawl(self, df_auctions) -> List[str]:
        
        # CRAWLING TO DO 
        to_crawl = df_auctions.loc[df_auctions[self.name.url_auction] != "MISSING_URL_AUCTION", 
                                    self.name.url_auction].drop_duplicates().tolist()
        
        return to_crawl

    def get_page_number(self, driver):
        page_nbr = self.get_elements(driver, "XPATH", "//div[@class='pager__count-wrapper']/div")
        if len(page_nbr) !=0:
            try:
                nbr_pages = int(page_nbr[-1].text.replace("of", "").strip())
                self._log.info(f"PAGINATION NUMBER IS= {page_nbr[-1].text}")
            except Exception as e:
                self._log.error(f"PAGINATION NUMBER IS= {page_nbr[-1].text.replace("of", "").strip()} \n {e}")
                nbr_pages = 1 
        else:
            nbr_pages =1
        return nbr_pages

    def crawl_iteratively_seller(self, driver, config: DictConfig):

        # crawl infos 
        list_infos = []
        page_nbr = self.get_page_number(driver)
        url = driver.current_url

        for i in range(1, page_nbr+1):
            if i == 1:
                url = url + "/page1"
            if i != 1:
                self.get_url(driver, url.replace(f"/page{i-1}", f"/page{i}"))
                
            new_infos = self.crawl_iteratively(driver, config)
            list_infos = list_infos + new_infos

        return list_infos