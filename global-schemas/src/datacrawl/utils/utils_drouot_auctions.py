from typing import Dict
from omegaconf import DictConfig
from datetime import datetime
import tqdm

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling


class DrouotAuctions(Crawling):

    def __init__(self, context: Context, config: DictConfig):

        super().__init__(context=context, config=config)
        self.history_start_year = self._config.crawling["drouot"].history_start_year

    def urls_to_crawl(self, start_date, end_date, url_auctions):
        url_auctions = self.define_auction_url(start_date, end_date, url_auctions)
        nbr_pages = self.get_nbr_auction_pages(url_auctions)
        to_crawl = self.get_pages_url(nbr_pages, url_auctions)
        return to_crawl

    def define_auction_url(self, start_date, end_date, url_auctions):

        if isinstance(start_date, datetime):
            year_start = start_date.year
            start_date = start_date.strftime("%d/%m/%Y")
        else:
            raise Exception("start date must be a datetime format")

        if isinstance(end_date, datetime):
            end_date = end_date.strftime("%d/%m/%Y")
        else:
            raise Exception("start date must be a datetime format")

        if year_start != self.history_start_year:
            url_auctions = (
                url_auctions
                + f"""&actuDatefilter={start_date}+-+{end_date}&""".replace("/", "%2F")
            )
        return url_auctions

    def get_nbr_auction_pages(self, url_auctions):
        driver = self.initialize_driver_chrome()
        driver.get(url_auctions)

        page_nbr = self.get_elements(
            driver, "XPATH", "//span[@class='lnk directNextStep']"
        )
        try:
            nbr_pages = int(page_nbr[-1].text)
            self._log.info(f"PAGINATION NUMBER IS= {page_nbr[-1].text}")
        except Exception as e:
            self._log.error(f"PAGINATION NUMBER IS= {page_nbr[-1].text} \n {e}")
            nbr_pages = 0

        driver.close()
        return nbr_pages

    def get_pages_url(self, nbr_pages, url_auctions):
        return [url_auctions + f"page={x}" for x in range(1, nbr_pages + 1)]

    def crawl_iteratively(self, driver, config: Dict):

        # crawl infos
        list_infos = []
        liste_lots = self.get_elements(
            driver, config.liste_elements.by_type, config.liste_elements.value_css
        )

        # save pict
        for lot in tqdm.tqdm(liste_lots[1:]):
            lot_info = {}

            try:
                lot_info[self.name.url_auction] = self.get_url_auctions(lot)
                new_info = self.extract_element_infos(lot, config.per_element)
                lot_info.update(new_info)
                list_infos.append(lot_info)

            except Exception as e:
                self._log.warning(f"ERROR happened for URL {driver.current_url} - {e}")

        return list_infos

    def get_url_auctions(self, driver):
        all_hrefs = self.get_elements(driver, "TAG_NAME", "a")
        links = [x.get_attribute("href") for x in all_hrefs]
        links = [x for x in links if x and "modal-content" not in x]
        if len(links) != 0:
            return links[0]
        else:
            return "MISSING_URL_AUCTION"
