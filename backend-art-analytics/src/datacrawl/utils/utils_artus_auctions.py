
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling


class ArtusAuctions(Crawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)
        self.history_start_year = self._config.crawling[self.seller].history_start_year

    def urls_to_crawl(self, start_date, end_date, url_auctions):
        to_crawl = []
        start_year = max(start_date.year, self.history_start_year)

        for year in range(start_year, end_date.year + 1):
            for offset in range(0, 500, 50):
                to_crawl.append(url_auctions + f"?offset={offset}&year={year}")
        return to_crawl