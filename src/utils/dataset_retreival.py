
import logging
from src.context import Context 
from omegaconf import DictConfig
from src.utils.step import Step
from src.utils.timing import timing
import pandas as pd 

class DatasetRetreiver(Step):

    def __init__(
            self,
            config : DictConfig,
            context : Context, 
    ):
        super().__init__(config=config, context=context)

    def get_text_to_cluster(self, data_name:str=None):

        if data_name==None:
            data_name="PICTURES_CATEGORY_20_04_2024"

        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_text_to_cluster"))
        formatted_query = self.sql_queries.format_query(
                raw_query,
                {
                    "id_item": self.name.id_item,
                    "table_name": data_name,
                    "class_prediction" : "TOP_0",
                    "picture_path": "PICTURES",
                    "text_vector": self.name.total_description,
                    "proba_var" : "PROBA_0",
                    "proba_threshold": 0.9,
                },
            )

        # 3. Fetch results
        logging.info(formatted_query)
        return self.read_sql_data(formatted_query)
    
    def get_text_to_cluster(self, data_name:str=None):

        if data_name==None:
            data_name="PICTURES_CATEGORY_20_04_2024"

        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_text_to_cluster"))
        formatted_query = self.sql_queries.format_query(
                raw_query,
                {
                    "id_item": self.name.id_item,
                    "table_name": data_name,
                    "class_prediction" : "TOP_0",
                    "picture_path": "PICTURES",
                    "text_vector": self.name.total_description,
                    "proba_var" : "PROBA_0",
                    "proba_threshold": 0,
                },
            )

        # 3. Fetch results
        logging.info(formatted_query)
        return self.read_sql_data(formatted_query)
    
    @timing
    def get_all_dataframes(self)-> pd.DataFrame:
        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_sellers_dataframe"))
        formatted_query = self.sql_queries.format_query(
                raw_query,
                {
                    "drouot_name": self._config.cleaning.drouot.origine_table_name,
                    "christies_name": self._config.cleaning.christies.origine_table_name,
                    "sothebys_name": self._config.cleaning.sothebys.origine_table_name,
                    "id_item": self.name.id_item,
                    "id_picture": self.name.id_picture,
                    "lot": self.name.lot,
                    "date": self.name.date,
                    "localisation": self.name.localisation,
                    "seller": self.name.seller,
                    "type_sale": self.name.type_sale,
                    "url_full_detail": self.name.url_full_detail,
                    "auction_title": self.name.auction_title,
                    "item_title": self.name.item_title,
                    "detailed_title": self.name.detailed_title,
                    "item_description": self.name.item_description,
                    "detailed_description": self.name.detailed_description,
                    "min_estimate": self.name.min_estimate,
                    "max_estimate": self.name.max_estimate,
                    "item_result": self.name.item_result,
                    "is_item_result": self.name.is_item_result,
                    "currency": self.name.currency
                },
            )

        # 3. Fetch results
        self._log.info(formatted_query)
        return self.read_sql_data(formatted_query)
    
    def get_all_pictures(self, data_name:str=None):

        if data_name==None:
            data_name="ALL_ITEMS_202403"

        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_all_pictures_and_infos"))
        formatted_query = self.sql_queries.format_query(
                raw_query,
                {
                    "table_name": data_name,
                    "id_item": self.name.id_item,
                    "id_picture": self.name.id_picture,
                    "date": self.name.date,
                    "localisation": self.name.localisation,
                    "seller": self.name.seller,
                    "type_sale": self.name.type_sale,
                    "url_full_detail": self.name.url_full_detail,
                    "auction_title": self.name.auction_title,
                    "total_description": self.name.total_description,
                    "min_estimate": self.name.min_estimate,
                    "max_estimate": self.name.max_estimate,
                    "item_result": self.name.item_result,
                    "eur_min_estimate": self.name.eur_min_estimate,
                    "eur_max_estimate": self.name.eur_max_estimate,
                    "eur_item_result": self.name.eur_item_result,
                    "is_item_result": self.name.is_item_result,
                    "currency": self.name.currency,
                    "country": self.name.country
                },
            )

        # 3. Fetch results
        logging.info(formatted_query)
        return self.read_sql_data(formatted_query)