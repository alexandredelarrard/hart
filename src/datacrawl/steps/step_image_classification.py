from typing import Dict
import pandas as pd 
from typing import List

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from omegaconf import DictConfig


class StepImageClassification(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)

        self.sql_table_name = "MANUAL_CLUSTER"
        
    @timing
    def run(self):

        df_cluster = pd.read_sql(self.sql_table_name, con=self._context.db_con)