from typing import Dict
import pandas as pd 
from typing import List

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.TrainerLightgbm import TrainLightgbmModel

from omegaconf import DictConfig

class StepPriceEvaluator(TrainLightgbmModel):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 category : str = "vase"):

        super().__init__(context=context, config=config, category=category)
        self.category = category

    def training(self, database_name):

        df = self.read_sql_data(database_name)
        df_price = self.get_pricing_info()

    def get_pricing_info(self):

        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_all_for_pricing"))
        formatted_query = self.sql_queries.format_query(
                raw_query,
                {
                    "id_item": self.name.id_item,
                    "eur_min_estimate" : self.name.eur_min_estimate,
                    "eur_max_estimate" : self.name.eur_max_estimate,
                    "eur_item_result" : self.name.eur_item_result,
                    "currency" : self.name.currency,  
                    "auction_date" : self.name.date, 
                    "localisation" : self.name.localisation, 
                    "seller" : self.name.seller,
                    "table_name_full": self._config.cleaning.full_data_auction_houses         
                },
            )

        # 3. Fetch results
        self._log.info(formatted_query)
        return self.read_sql_data(formatted_query)
        