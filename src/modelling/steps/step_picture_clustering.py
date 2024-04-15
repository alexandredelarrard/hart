import os 
from tqdm import tqdm
from glob import glob 
import pandas as pd 

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.Clustering import TopicClustering
from src.modelling.transformers.Embedding import StepEmbedding
from src.utils.utils_crawler import (copy_picture, move_picture)
from src.modelling.transformers.ChromaCollection import ChromaCollection

from src.constants.variables import (CHROMA_PICTURE_DB_NAME)

from omegaconf import DictConfig

class StepPictureClustering(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 save_embeddings : bool = False):

        super().__init__(context=context, config=config)

        self.save_pictures = True
        self.save_embeddings = save_embeddings
        self.reduce_dimension = False
        
        self.params = self._config.embedding.clustering.params
        self.n_words_cluster = self.params.n_words_cluster

        self.step_cluster = TopicClustering(params=self.params)
        self.step_embedding = StepEmbedding(context=context, config=config, 
                                            type="picture")
        
    @timing
    def run(self, data_name : str):

        #exrtract data from dbeaver
        data_name = "TEST_0.05_06_04_2024_12_04_2024"
        self.vector = "PICTURES"
        df_desc = self.get_data(data_name)
        df_desc = self.check_is_file(df_desc)

        liste_picts = glob(r"D:\data\pictures_training\tableau\*.jpg") + glob(r"D:\data\test\tableau\*.jpg")
        df_desc = pd.DataFrame(liste_picts, columns = ["PICTURES"])

        # create text embedding
        self.embeddings = self.step_embedding.get_batched_picture_embeddings(df_desc[self.vector].tolist())
        
        if self.reduce_dimension:
            self.reduced_embedding = self.step_embedding.embedding_reduction(self.embeddings, 
                                                                    method_dim_reduction="umap")

            # get cluster 
            df_desc[self.name.cluster_id] = self.step_cluster.hdbscan_clustering(self.reduced_embedding)

        else:
            df_desc[self.name.cluster_id] = self.step_cluster.hdbscan_clustering(self.embeddings)

        if self.save_pictures:
            self.save_clustered_pictures(df_desc)
            
        if self.params["verbose"] ==1:
            plot_reduced_embedding = self.step_embedding.embedding_reduction(self.embeddings, 
                                                                             method_dim_reduction="tsne")
            df_desc["x"], df_desc["y"] = zip(*plot_reduced_embedding)
            self.step_cluster.plot_clusters(df_desc)

        if self.save_embeddings:
            chroma_collection = ChromaCollection(context=self._context,
                                                 data_name=CHROMA_PICTURE_DB_NAME, 
                                                 config=self._config)
            chroma_collection.save_collection(df_desc, self.embeddings)

        return df_desc 
    
    @timing
    def check_is_file(self, df):
        exists_pict = df["PICTURES"].swifter.apply(lambda x : os.path.isfile(x))
        df = df[exists_pict].reset_index(drop=True)
        return df
    
    @timing
    def save_clustered_pictures(self,sub_df):
        sub_df = sub_df.loc[sub_df[self.name.cluster_id] != -1]
        sub_df["TO"] = sub_df[self.name.cluster_id].apply(lambda x : f"D:/data/other/{str(x)}")
        for row in tqdm(sub_df.to_dict(orient="records")):
            move_picture(row["PICTURES"], row["TO"])

    @timing
    def get_data(self, data_name):
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
        self._log.info(formatted_query)
        return self.read_sql_data(formatted_query)
