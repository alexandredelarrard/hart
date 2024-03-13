from typing import Dict
import pandas as pd 

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.datacrawl.transformers.Clustering import TopicClustering
from src.datacrawl.transformers.Embedding import StepEmbedding

from omegaconf import DictConfig


class StepTextClustering(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 database_name : str = "drouot",
                 vector : str = "DESCRIPTION"):

        super().__init__(context=context, config=config)

        self.vector = vector

        self.params = self._config.embedding[database_name].clustering.params
        self.prompt_name = self._config.embedding[database_name].prompt_name
        self.sql_table_name = self._config.embedding[database_name].origine_table_name
        
        self.step_cluster = TopicClustering(params=self.params)
        self.step_embedding = StepEmbedding(context=context, config=config, 
                                            database_name=database_name)
        
    @timing
    def run(self):

        df_desc = self.get_data()
        embeddings = self.step_embedding.get_embeddings(df_desc[self.vector],
                                                        prompt_name=self.prompt_name)
        reduced_embedding = self.step_embedding.embedding_reduction(embeddings, 
                                                                    method_dim_reduction="umap")

        df_desc["labels"] = self.step_cluster.hdbscan_clustering(reduced_embedding)

        if self.params["verbose"] ==1:
            plot_reduced_embedding = self.step_embedding.embedding_reduction(embeddings, 
                                                                        method_dim_reduction="tsne")
            df_desc["x"], df_desc["y"] = zip(*plot_reduced_embedding)
            self.step_cluster.plot_clusters(df_desc)

    def get_data(self):
        return pd.read_sql(f"SELECT * FROM \"{self.sql_table_name}\" LIMIT 10000", 
                           con=self._context.db_con)
    
    