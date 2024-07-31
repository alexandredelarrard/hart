from typing import Dict, List
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling


class ChristiesItems(Crawling):

    def __init__(self, context: Context, config: DictConfig):

        super().__init__(context=context, config=config)
        self.root_path = self._context.paths["ROOT"]

    # Update each URL and add to new_to_crawl list
    def urls_to_crawl(self, to_crawl: List[dict]):
        return [
            {
                **element,
                "url": (
                    element["url"][:-1]
                    if element["url"].endswith("/")
                    else element["url"]
                )
                + "/?loadall=true",
            }
            for element in to_crawl
        ]

    def crawl_iteratively_seller(self, driver, config: Dict):
        return super().crawl_iteratively(driver, config)
