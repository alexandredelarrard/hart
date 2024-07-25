from typing import Dict
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling


class ChristiesItems(Crawling):

    def __init__(self, context: Context, config: DictConfig):

        super().__init__(context=context, config=config)
        self.root_path = self._context.paths["ROOT"]
        self.to_replace = ("&page=2&sortby=lotnumber", "/?loadall=true")
        self.to_split = []

    # second crawling step  to get list of pieces per auction
    def urls_to_crawl(self, to_crawl):

        # AUCTIONS
        to_crawl = [x[:-1] if x[-1] == "/" else x for x in to_crawl]
        return [x + "/?loadall=true" for x in to_crawl]

    def crawl_iteratively_seller(self, driver, config: Dict):
        return super().crawl_iteratively(driver, config)
