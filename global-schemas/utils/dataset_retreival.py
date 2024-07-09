import logging
import pandas as pd
from omegaconf import DictConfig
from typing import List

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from src.constants.variables import TEXT_DB_EN, TEXT_DB_FR, PICTURE_DB


class DatasetRetreiver(Step):

    def __init__(
        self,
        config: DictConfig,
        context: Context,
    ):
        super().__init__(config=config, context=context)
        self.root = self._config.crawling.root_path
        self.full_items_and_pictures = self._config.cleaning.full_data_auction_houses
        self.full_per_item = self._config.cleaning.full_data_per_item

    def get_text_to_cluster(self, data_name: str = None):

        if data_name == None:
            data_name = "PICTURES_CATEGORY_20_04_2024"

        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_text_to_cluster"))
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {
                "id_item": self.name.id_item,
                "table_name": data_name,
                "class_prediction": "TOP_0",
                "picture_path": "PICTURES",
                "text_vector": self.name.total_description,
                "proba_var": "PROBA_0",
                "proba_threshold": 0.9,
            },
        )

        # 3. Fetch results
        logging.info(formatted_query)
        return self.read_sql_data(formatted_query)

    def get_text_to_cluster(self, data_name: str = None):

        if data_name == None:
            data_name = "PICTURES_CATEGORY_20_04_2024"

        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_text_to_cluster"))
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {
                "id_item": self.name.id_item,
                "table_name": data_name,
                "class_prediction": "TOP_0",
                "picture_path": "PICTURES",
                "text_vector": self.name.total_description,
                "proba_var": "PROBA_0",
                "proba_threshold": 0,
            },
        )

        # 3. Fetch results
        logging.info(formatted_query)
        return self.read_sql_data(formatted_query)

    @timing
    def get_all_dataframes(self) -> pd.DataFrame:
        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_sellers_dataframe"))
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {
                "drouot_name": self._config.cleaning.drouot.origine_table_name.history,
                "christies_name": self._config.cleaning.christies.origine_table_name.history,
                "sothebys_name": self._config.cleaning.sothebys.origine_table_name.history,
                "millon_name": self._config.cleaning.millon.origine_table_name.history,
                "id_unique": self.name.id_unique,
                "id_item": self.name.id_item,
                "id_picture": self.name.id_picture,
                "url_full_detail": self.name.url_full_detail,
                "url_auction": self.name.url_auction,
                "lot": self.name.lot,
                "date": self.name.date,
                "localisation": self.name.localisation,
                "seller": self.name.seller,
                "house": self.name.house,
                "type_sale": self.name.type_sale,
                "auction_title": self.name.auction_title,
                "detailed_title": self.name.detailed_title,
                "total_description": self.name.total_description,
                "min_estimate": self.name.min_estimate,
                "max_estimate": self.name.max_estimate,
                "item_result": self.name.item_result,
                "currency": self.name.currency,
                "is_item_result": self.name.is_item_result,
                "is_picture": self.name.is_picture,
            },
        )

        # 3. Fetch results
        self._log.info(formatted_query)
        return self.read_sql_data(formatted_query)

    @timing
    def get_all_new_dataframes(self) -> pd.DataFrame:
        raw_query = str.lower(
            getattr(self.sql_queries.SQL, "get_sellers_new_dataframe")
        )
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {
                "drouot_name": self._config.cleaning.drouot.origine_table_name.new,
                "christies_name": self._config.cleaning.christies.origine_table_name.new,
                "sothebys_name": self._config.cleaning.sothebys.origine_table_name.new,
                "millon_name": self._config.cleaning.sothebys.origine_table_name.new,
                "id_unique": self.name.id_unique,
                "id_item": self.name.id_item,
                "id_picture": self.name.id_picture,
                "url_full_detail": self.name.url_full_detail,
                "url_auction": self.name.url_auction,
                "lot": self.name.lot,
                "date": self.name.date,
                "localisation": self.name.localisation,
                "seller": self.name.seller,
                "house": self.name.house,
                "type_sale": self.name.type_sale,
                "auction_title": self.name.auction_title,
                "detailed_title": self.name.detailed_title,
                "total_description": self.name.total_description,
                "min_estimate": self.name.min_estimate,
                "max_estimate": self.name.max_estimate,
                "item_result": self.name.item_result,
                "currency": self.name.currency,
                "is_item_result": self.name.is_item_result,
                "is_picture": self.name.is_picture,
            },
        )

        # 3. Fetch results
        self._log.info(formatted_query)
        return self.read_sql_data(formatted_query)

    @timing
    def get_all_pictures(
        self, data_name: str = None, vector: str = "PICTURES", limit: int = None
    ):

        if data_name == None:
            data_name = self.full_items_and_pictures

        if not limit:
            limit = 1e11

        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_all_pictures"))
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {
                "table_name": data_name,
                "id_unique": self.name.id_unique,
                "id_item": self.name.id_item,
                "id_picture": self.name.id_picture,
                "seller": self.name.seller,
                "is_picture": self.name.is_picture,
                "total_description": self.name.total_description,
                "base_path": self.root,
                "limite": limit,
            },
        )

        # 3. Fetch results
        logging.info(formatted_query)
        df = self.read_sql_data(formatted_query)
        df[vector] = df[[self.name.id_picture, self.name.seller]].apply(
            lambda x: "/".join(
                [
                    self.root,
                    x[self.name.seller],
                    "pictures",
                    x[self.name.id_picture] + ".jpg",
                ]
            ),
            axis=1,
        )
        logging.info(f"GETTING {df.shape}")
        return df

    def get_all_text(
        self, data_name: str = None, language: str = None, limit: int = None
    ):

        if data_name == None:
            data_name = self.full_per_item

        if not limit:
            limit = 1e11

        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_all_text"))
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {
                "table_name": data_name,
                "id_item": self.name.id_item,
                "title": language + "_TITLE",
                "description": language + "_DESCRIPTION",
                "limite": limit,
            },
        )

        # 3. Fetch results
        logging.info(formatted_query)
        df = self.read_sql_data(formatted_query)
        logging.info(f"GETTING {df.shape}")
        return df

    @timing
    def get_picture_embedding_dist(self, embedding: str = None, limit: int = None):

        if not limit:
            limit = 100

        raw_query = str.lower(getattr(self.sql_queries.SQL, "picture_embedding_dist"))
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {  # because embedding table need lower
                "id_unique_lower": self.name.id_unique.lower(),
                "id_picture_lower": self.name.id_picture.lower(),
                "table": PICTURE_DB,
                "limite": limit,
            },
        )

        # 3. Fetch results
        df = self.read_sql_data(formatted_query, params=(embedding.tolist()[0],))
        return df

    @timing
    def get_id_item_from_pictures(self, list_id_unique: List[str]):

        raw_query = str.lower(getattr(self.sql_queries.SQL, "id_item_from_id_unique"))
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {  # because embedding table need lower
                "id_item": self.name.id_item,
                "id_unique": self.name.id_unique,
                "table": self.full_items_and_pictures,
                "liste_id_unique": tuple(list_id_unique),
            },
        )

        # 3. Fetch results
        df = self.read_sql_data(formatted_query)
        df.columns = [x.lower() for x in df.columns]

        return df

    @timing
    def get_text_embedding_dist(
        self, table: str, embedding: str = None, limit: int = None
    ):

        if not limit:
            limit = 100

        raw_query = str.lower(getattr(self.sql_queries.SQL, "text_embedding_dist"))
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {
                "id_item_lower": self.name.id_item.lower(),
                "table": table,
                "limite": limit,
            },
        )

        # 3. Fetch results
        df = self.read_sql_data(formatted_query, params=(embedding.tolist()[0],))
        return df
