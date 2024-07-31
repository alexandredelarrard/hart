from datetime import datetime
from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawling import Crawling
from src.utils.utils_crawler import (
    save_picture_crawled,
    save_canvas_picture,
    define_save_paths,
)
from src.schemas.crawling_schemas import Pictures


class StepCrawlingPictures(Crawling):

    def __init__(
        self,
        context: Context,
        config: DictConfig,
        threads: int,
        seller: str = "christies",
    ):

        self.today = datetime.today()
        self.seller = seller
        self.paths = define_save_paths(config, self.seller)
        kwargs = {"is_picture": False, "is_javascript": False, "is_cookie": False}

        super().__init__(
            context=context,
            config=config,
            threads=threads,
            save_queue_path=self.paths["pictures"],
            kwargs=kwargs,
        )

        self.sql_pictures_table_raw = Pictures.__tablename__
        self._infos = self._config.crawling[self.seller]

    # second crawling step  to get list of pieces per auction
    def get_list_items_to_crawl(self):

        # extract all picture urls to crawl from details dataframes
        df_pictures = self.read_sql_data(
            f"""SELECT "{self.name.url_picture}" as url, {self.name.id_picture}
                FROM {self.sql_pictures_table_raw}
                WHERE "{self.name.seller}"='{self.seller}'
                    AND "{self.name.is_file}" = false """
        )

        return df_pictures.to_dict(orient="records")

    def crawling_picture(self, driver, kwargs):

        # crawl detail of one url
        url = driver.current_url
        if self.name.low_id_picture in kwargs.keys():
            picture_id = kwargs[self.name.low_id_picture]
        else:
            raise Exception(
                f"Should have passed {self.name.low_id_picture} info along url, got {kwargs}"
            )

        # save pictures & infos
        is_path = save_picture_crawled(url, self.paths["pictures"], picture_id)

        query = f"""UPDATE {self.sql_pictures_table_raw}
                    SET "{self.name.is_file}" = {is_path}
                    WHERE "{self.name.low_id_picture}"='{picture_id}' """
        self.update_raw_to_table(query)

        return driver, is_path

    def crawling_canvas(self, driver, kwargs):

        # crawl detail of one url
        if self.name.low_id_picture in kwargs.keys():
            picture_id = kwargs[self.name.low_id_picture]
        else:
            raise Exception(
                f"Should have passed {self.name.low_id_picture} info along url, got {kwargs}"
            )

        if "pictures" not in self._infos.keys():
            raise Exception(
                "Need to provide crawling infos on picture when using mode canvas"
            )

        # save pictures & infos
        list_infos = self.crawl_iteratively(driver, self._infos["pictures"])
        message = save_canvas_picture(
            list_infos["URL_PICTURE_CANVAS"], self.paths["pictures"], picture_id
        )

        return driver, message
