from omegaconf import DictConfig
from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling

class DetailsUtils(Crawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 seller: str):
        
        super().__init__(context=context, config=config)
        self.seller = seller

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
    
    def crawling_details_function(self, driver, config):
        try:
            infos = eval(f"self.crawl_iteratively_{self.seller}_detail(driver=driver, config=config)")
        except Exception as e:
            self._log.debug(e)
            infos = self.crawl_iteratively(driver=driver, config=config)
        return driver, infos