from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.Clustering import TopicClustering
from src.modelling.transformers.Embedding import StepEmbedding
from src.modelling.transformers.NlpToolBox import NLPToolBox
from src.utils.utils_crawler import copy_picture

from omegaconf import DictConfig

class StepPictureClustering(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 save_embeddings : bool = False):

        super().__init__(context=context, config=config)

        self.n_top_results = 20
        self.save_pictures = True
        self.save_embeddings = save_embeddings
        
        self.params = self._config.embedding.clustering.params
        self.n_words_cluster = self.params.n_words_cluster

        self.step_cluster = TopicClustering(params=self.params)
        self.step_embedding = StepEmbedding(context=context, config=config, 
                                            type="picture")
        
    @timing
    def run(self, data_name : str, vector : str):

        #exrtract data from dbeaver
        # data_name = "TEST_0.05_06_04_2024"
        # vector = "PICTURES"
        self.vector = vector
        df_desc = self.get_data(data_name)

        sub_df= df_desc.loc[df_desc["TOP_0"] == "vase"]

        # create text embedding
        self.embeddings = self.step_embedding.get_batched_picture_embeddings(sub_df[self.vector].tolist())
        
        self.reduced_embedding = self.step_embedding.embedding_reduction(self.embeddings, 
                                                                    method_dim_reduction="umap")

        # get cluster 
        sub_df[self.name.cluster_id] = self.step_cluster.hdbscan_clustering(self.reduced_embedding)

        if self.save_pictures:
            sub_df = sub_df.loc[sub_df[self.name.cluster_id] != -1]

            sub_df["TO"] = sub_df[self.name.cluster_id].apply(lambda x : "./data/other/" + "vase_" + str(x))
            for row in sub_df.to_dict(orient="records"):
                copy_picture(row[self.vector], row["TO"])

        if self.params["verbose"] ==1:
            plot_reduced_embedding = self.step_embedding.embedding_reduction(self.embeddings, 
                                                                             method_dim_reduction="tsne")
            df_desc["x"], df_desc["y"] = zip(*plot_reduced_embedding)
            self.step_cluster.plot_clusters(df_desc)

        if self.save_embeddings:
            self.collection = self._context.chroma_db.get_or_create_collection(
                                    name = data_name,
                                    metadata={"hnsw:space": "cosine"})
            self.save_collection(df_desc, self.embeddings)

        return df_desc 
    
    def get_data(self, data_name):
        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_text_to_cluster"))
        formatted_query = self.sql_queries.format_query(
                raw_query,
                {
                    "id_item": self.name.id_item,
                    "table_name": data_name,
                    "picture_path": "PICTURES",
                    "class_prediction" : "TOP_0",
                    "text_vector": self.vector,
                    "proba_var" : "PROBA_0",
                    "proba_threshold": 0.9         
                },
            )

        # 3. Fetch results
        self._log.info(formatted_query)
        return self.read_sql_data(formatted_query)
