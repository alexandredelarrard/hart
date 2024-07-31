import logging
import pandas as pd
from omegaconf import DictConfig
from typing import List

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.schemas.gpt_cleaning import GptTranslateCategorize
from src.schemas.gpt_schemas import LlmExtraction
from src.constants.variables import TEXT_DB_EN, TEXT_DB_FR, PICTURE_DB
from src.schemas.crawling_schemas import Pictures
from src.schemas.crawling_cleaning import AllItems


class DatasetRetreiver(Step):

    def __init__(
        self,
        config: DictConfig,
        context: Context,
    ):
        super().__init__(config=config, context=context)
        self.root = self._context.paths["ROOT"]

    @timing
    def get_all_pictures(self, limit: int = None):

        if not limit:
            limit = 1e11

        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_all_pictures"))
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {
                "table_name": Pictures.__tablename__,
                "id_picture": self.name.low_id_picture,
                "seller": self.name.seller,
                "is_file": self.name.is_file,
                "picture_embedding_table": self._config.table_names.picture_embeddings,
                "limite": limit,
                "root": self.root,
            },
        )

        # 3. Fetch results
        logging.info(formatted_query)
        df = self.read_sql_data(formatted_query)
        logging.info(f"GETTING {df.shape}")
        return df

    def get_all_text(self, limit: int = None, embedding_table_name: str = TEXT_DB_EN):

        if embedding_table_name == TEXT_DB_FR:
            language = "french"
        elif embedding_table_name == TEXT_DB_EN:
            language = "english"
        else:
            raise Exception("Can only handle french or english languages so far")

        if not limit:
            limit = 1e11

        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_all_text"))
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {
                "table_name": GptTranslateCategorize.__tablename__,
                "id_item": self.name.low_id_item,
                "detail_title": language + "_title",
                "total_description": language + "_description",
                "text_embedding_table": embedding_table_name,
                "limite": limit,
                "string_limit": 25,  # number minimal characters to embed a text
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
                "id_picture": self.name.low_id_picture,
                "list_id_item": self.name.list_id_item,
                "table": PICTURE_DB,
                "limite": limit,
                "picture_table": Pictures.__tablename__,
            },
        )

        # 3. Fetch results
        df = self.read_sql_data(formatted_query, params=(embedding.tolist()[0],))
        return df

    @timing
    def get_text_embedding_dist(
        self, table: str, embedding: str = None, limit: int = 100
    ):

        raw_query = str.lower(getattr(self.sql_queries.SQL, "text_embedding_dist"))
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {
                "id_item_lower": self.name.low_id_item,
                "table": table,
                "limite": limit,
            },
        )

        # 3. Fetch results
        return self.read_sql_data(formatted_query, params=(embedding.tolist()[0],))

    @timing
    def get_gpt_category_input(self):

        raw_query = str.lower(getattr(self.sql_queries.SQL, "gpt_category_input"))
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {
                "id_item": self.name.low_id_item,
                "item_title_detailed": self.name.detailed_title,
                "total_description": self.name.total_description,
                "table": AllItems.__tablename__,
                "raw_table_gpt": LlmExtraction.__tablename__,
                "id_item_gpt": LlmExtraction.model_fields["id_item"].name,
                "schema_prompt_col": LlmExtraction.model_fields["prompt_schema"].name,
                "schema_prompt_value": "reformulate",
            },
        )

        # 3. Fetch results
        return self.read_sql_data(formatted_query)

    @timing
    def get_gpt_object_extract_input(self, object_value: str, schema_prompt_value: str):

        raw_query = str.lower(getattr(self.sql_queries.SQL, "gpt_object_extract_input"))
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {
                "gpt_translate_categorize": GptTranslateCategorize.__tablename__,
                "id_item": GptTranslateCategorize.model_fields[
                    self.name.low_id_item
                ].name,
                "total_description": GptTranslateCategorize.model_fields[
                    self.name.input
                ].name,
                "english_title": GptTranslateCategorize.model_fields[
                    "english_title"
                ].name,
                "english_description": GptTranslateCategorize.model_fields[
                    "english_description"
                ].name,
                "category_object": GptTranslateCategorize.model_fields[
                    "clean_object_category"
                ].name,
                "object_value": object_value,
                "raw_table_gpt": LlmExtraction.__tablename__,
                "id_item_gpt": LlmExtraction.model_fields[self.name.low_id_item].name,
                "schema_prompt_col": LlmExtraction.model_fields[
                    self.name.prompt_schema
                ].name,
                "schema_prompt_value": schema_prompt_value,
            },
        )

        # 3. Fetch results
        return self.read_sql_data(formatted_query)
