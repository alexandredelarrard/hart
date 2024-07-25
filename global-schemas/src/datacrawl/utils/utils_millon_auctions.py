from omegaconf import DictConfig
import time

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling


class MillonAuctions(Crawling):

    def __init__(self, context: Context, config: DictConfig):

        super().__init__(context=context, config=config)
        self.history_start_year = self._config.crawling["millon"].history_start_year

    def new_urls(self, start_date, end_date, url_auctions, nbr_pages_done):
        nbr_pages = self.get_nbr_auction_pages(url_auctions)
        start_year = max(start_date.year, self.history_start_year)

        if start_date.year != self.history_start_year:
            pages_per_year = nbr_pages // (end_date.year - self.history_start_year)
            nbr_pages = int(pages_per_year * (end_date.year - start_year + 1))
        else:
            nbr_pages = nbr_pages - nbr_pages_done

        to_crawl = []
        for page in range(1, nbr_pages + 1):
            to_crawl.append(url_auctions + f"page{page}")
        return to_crawl

    def get_nbr_auction_pages(self, url_auctions):

        driver = self.initialize_driver_chrome()
        self.get_url(driver, url_auctions)

        page_nbr = self.get_elements(
            driver, "XPATH", "//div[@class='pager__count-wrapper']/div"
        )
        try:
            nbr_pages = int(page_nbr[-1].text.replace("of", "").strip())
            self._log.info(f"PAGINATION NUMBER IS= {page_nbr[-1].text}")
        except Exception as e:
            self._log.error(
                f"PAGINATION NUMBER IS= {page_nbr[-1].text.replace('of', '').strip()} \n {e}"
            )
            nbr_pages = 0

        self.delete_driver(driver)
        return nbr_pages

    def urls_to_crawl(self, start_date, end_date, url_auctions, already_crawled):
        to_crawl = self.new_urls(
            start_date, end_date, url_auctions, nbr_pages_done=len(already_crawled)
        )
        return to_crawl
