import glob
import pandas as pd 
from typing import List

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.datacrawl.transformers.Clustering import TopicClustering
from src.datacrawl.transformers.Embedding import StepEmbedding

from omegaconf import DictConfig


class StepPictureClustering(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 database_name : str = "drouot",
                 vector : str = "DESCRIPTION"):

        super().__init__(context=context, config=config)

        self.n_top_results=20
        self.database_name = database_name
        self.vector= vector

        self.params = self._config.embedding[database_name].clustering.params
        self.sql_table_name = self._config.embedding[database_name].origine_table_name

        self.step_cluster = TopicClustering(params=self.params)
        self.step_embedding = StepEmbedding(context=context, config=config, 
                                            database_name=database_name,
                                            type="picture")
        
        self.collection = self._context.chroma_db.get_or_create_collection(
                                    name="PICTURE_" + self.database_name,
                                    metadata={"hnsw:space": "cosine"})
        
    @timing
    def run(self):

        df_desc = self.get_data()
        liste_pictures_path = self.get_pictures_path(df_desc)
        embeddings = self.step_embedding.get_batched_picture_embeddings(liste_pictures_path)
        
        reduced_embedding = self.step_embedding.embedding_reduction(embeddings, 
                                                                    method_dim_reduction="umap")

        df_desc["labels"] = self.step_cluster.hdbscan_clustering(reduced_embedding)

        if self.params["verbose"] ==1:
            plot_reduced_embedding = self.step_embedding.embedding_reduction(embeddings, 
                                                                        method_dim_reduction="tsne")
            df_desc["x"], df_desc["y"] = zip(*plot_reduced_embedding)
            self.step_cluster.plot_clusters(df_desc)

        self.save_collection(df_desc, embeddings)

    def get_data(self):
        return pd.read_sql(f"SELECT * FROM \"{self.sql_table_name}\" ", #LIMIT 50000
                           con=self._context.db_con)
    
    def get_pictures_path(self, df_desc):
        root_path = self._config.crawling[self.database_name].save_picture_path
        return df_desc["PICTURE_ID"].apply(lambda x : root_path + f"/{x}.jpg" if 
                                               "MISSING" not in x else 
                                               root_path + f"/MISSING.jpg.jpg").tolist()
    
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
    def query_collection(self, path_picture : str):

        if isinstance(path_picture, str):
            path_picture = [path_picture]

        elif isinstance(path_picture, List):
            path_picture = path_picture

        query_embedded = self.step_embedding.get_batched_picture_embeddings(path_picture)

        return self.collection.query(query_embeddings=query_embedded,
                                     n_results=self.n_top_results)

    