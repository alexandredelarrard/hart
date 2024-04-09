from typing import Dict
import pandas as pd 
from typing import List

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.NlpToolBox import NLPToolBox
from src.utils.utils_crawler import read_json

from omegaconf import DictConfig


class StepManualCluster(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 database_name : str = "drouot"):

        super().__init__(context=context, config=config)

        self.database_name = database_name
        self.vector = self._config.embedding[self.database_name].vector

        self.sql_table_name = self._config.embedding[self.database_name].origine_table_name
        self.output_table_name = "MANUAL_CLUSTER"
        self.manual_cluster =  self._config.embedding.manual_cluster

        self.nlp_tb = NLPToolBox()
        
    @timing
    def run(self):

        self.manuals = read_json(self.manual_cluster)

        vect = self.get_data()
        vect[self.vector] = self.nlp_tb.simple_homegenize(vect[self.vector])

        # words = self.nlp_tb.extract_top_n_words(vect[self.vector], ngram_range=(1,2))
        vect["MANUAL_CLUSTER"] = self.nlp_tb.manuak_clustering(vect[self.vector], self.manuals)
        # vect = vect.loc[vect["MANUAL_CLUSTER"].notnull()]

        # SAVE ITEMS ENRICHED
        self.write_sql_data(dataframe=vect,
                            table_name=self.output_table_name,
                            if_exists="replace")

    def get_data(self):
        return pd.read_sql(f"SELECT \"ID_ITEM\", \"{self.vector}\" FROM \"{self.sql_table_name}\" ", #LIMIT 50000
                           con=self._context.db_con)