import os 
from tqdm import tqdm
from typing import List

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.Clustering import TopicClustering
from src.modelling.transformers.Embedding import StepEmbedding
from src.utils.utils_crawler import move_picture
from src.utils.dataset_retreival import DatasetRetreiver
from src.modelling.transformers.ChromaCollection import ChromaCollection

from src.constants.variables import (CHROMA_PICTURE_DB_NAME)

from omegaconf import DictConfig

class StepPictureClustering(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 save_embeddings : bool = False):

        super().__init__(context=context, config=config)

        self.save_pictures = False
        self.save_embeddings = True
        self.reduce_dimension = False
        self.to_cluster = False
        self.vector = "PICTURES"
        
        self.params = self._config.embedding.clustering.params
        self.n_words_cluster = self.params.n_words_cluster

        self.step_cluster = TopicClustering(params=self.params)
        self.step_embedding = StepEmbedding(context=context, config=config, 
                                            type="picture")
        self.data_retreiver = DatasetRetreiver(context=context, config=config)
        self.chroma_collection = ChromaCollection(context=self._context,
                                                 data_name=CHROMA_PICTURE_DB_NAME, 
                                                 config=self._config)
        
    @timing
    def run(self):

        # exrtract data from dbeaver
        df_desc = self.data_retreiver.get_text_to_cluster(data_name="PICTURES_CATEGORY_20_04_2024")#get_all_pictures(data_name="ALL_ITEMS_202403")
        df_desc = self.check_is_file(df_desc)
        sub_df= df_desc.loc[df_desc["TOP_0"].isin(["dessin"])]
        # "tableau figuratif", "tableau moderne", "tableau portrait", "tableau nature_morte", "tableau religieux", "gravure", "dessin asiatique", 
        
        # create text embedding
        self.embeddings = self.get_picture_embedding(sub_df[self.vector].tolist())

        if self.to_cluster:
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
            self.chroma_collection.save_collection(df_desc, self.embeddings)

        return df_desc 
    
    def read_data_trained(self):
        df_desc = self.data_retreiver.get_text_to_cluster(data_name= "TEST_0.05_06_04_2024_12_04_2024")
        return df_desc

    def get_picture_embedding(self, picture_path):
         
        if isinstance(picture_path, str):
            picture_path = [picture_path]

        elif isinstance(picture_path, List):
            picture_path = picture_path

        else:
            raise Exception(f"Text need to be str or List[str] to be embedded intead of {picture_path.dtype}")

        return self.step_embedding.get_batched_picture_embeddings(picture_path)
        

    @timing
    def check_is_file(self, df_desc):
        if self.vector not in df_desc.columns:
            df_desc[self.vector] = df_desc[["SELLER", "ID_PICTURE"]].apply(lambda x : f"D:/data/{x['SELLER']}/pictures/{x['ID_PICTURE']}.jpg", axis=1)
        
        exists_pict = df_desc[self.vector].swifter.apply(lambda x : os.path.isfile(x))
        df_desc = df_desc[exists_pict].reset_index(drop=True)
        return df_desc
    
    @timing
    def save_clustered_pictures(self,sub_df):
        sub_df = sub_df.loc[sub_df[self.name.cluster_id] != -1]
        sub_df["TO"] = sub_df[self.name.cluster_id].apply(lambda x : f"D:/data/other/{str(x)}")
        for row in tqdm(sub_df.to_dict(orient="records")):
            move_picture(row["PICTURES"], row["TO"])

    
