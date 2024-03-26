from typing import Dict
import pandas as pd 
from typing import List

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
                 save_embeddings : bool = False):

        super().__init__(context=context, config=config)

        self.n_top_results = 20
        
        self.database_name = database_name
        self.save_embeddings = save_embeddings

        self.vector = self._config.embedding[database_name].vector
        self.params = self._config.embedding[database_name].clustering.params
        self.prompt_name = self._config.embedding[database_name].text.prompt_name
        self.sql_table_name = self._config.embedding[database_name].origine_table_name

        self.step_cluster = TopicClustering(params=self.params)
        self.step_embedding = StepEmbedding(context=context, config=config, 
                                            database_name=database_name,
                                            type="text")
        if self.save_embeddings:
            self.collection = self._context.chroma_db.get_or_create_collection(
                                    name = self.database_name,
                                    metadata={"hnsw:space": "cosine"})
        
    @timing
    def run(self):

        df_desc = self.get_data()

        self.embeddings = self.step_embedding.get_text_embeddings(df_desc[self.vector],
                                                        prompt_name=self.prompt_name)
        
        self.reduced_embedding = self.step_embedding.embedding_reduction(self.embeddings, 
                                                                    method_dim_reduction="umap")

        df_desc["labels"] = self.step_cluster.hdbscan_clustering(self.reduced_embedding)

        if self.params["verbose"] ==1:
            plot_reduced_embedding = self.step_embedding.embedding_reduction(self.embeddings, 
                                                                             method_dim_reduction="tsne")
            df_desc["x"], df_desc["y"] = zip(*plot_reduced_embedding)
            self.step_cluster.plot_clusters(df_desc)

        if self.save_embeddings:
            self.save_collection(df_desc, self.embeddings)

        return df_desc


    def get_data(self):
        return pd.read_sql(f"SELECT * FROM \"{self.sql_table_name}\" ", #LIMIT 50000
                           con=self._context.db_con)
    
    @timing
    def save_collection(self, df_desc, embeddings):

        step_size=41000 # max batch size collection step size
        nbr_steps = df_desc.shape[0] //step_size + 1

        for i in range(nbr_steps):
            self._log.info(f"[DB EMBEDDING] : adding batch {i} / {nbr_steps} to chromadb")
            sub_df = df_desc.iloc[i*step_size:(i+1)*step_size]
            self.collection.add(
                embeddings=embeddings[i*step_size:(i+1)*step_size],
                documents=sub_df[self.vector].tolist(),
                metadatas=sub_df.to_dict(orient="records"),
                ids=sub_df["ID"].tolist()
            )
    
    @timing
    def query_collection(self, query_text):

        if isinstance(query_text, str):
            query_text = [query_text]

        elif isinstance(query_text, List):
            query_text = query_text

        query_embedded = self.step_embedding.get_text_embeddings(query_text, 
                                                prompt_name=self.prompt_name)

        return self.collection.query(query_embeddings=query_embedded,
                                     n_results=self.n_top_results)

    