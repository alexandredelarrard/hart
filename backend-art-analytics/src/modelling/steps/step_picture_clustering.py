import os 
from tqdm import tqdm
from typing import List
import pandas as pd

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.Clustering import TopicClustering
from src.utils.utils_crawler import copy_picture
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
        self.reduce_dimension = False
        self.vector = "PICTURES"
        
        self.params = self._config.embedding.clustering.params
        self.n_words_cluster = self.params.n_words_cluster

        self.step_cluster = TopicClustering(params=self.params)
        self.chroma_collection = ChromaCollection(context=self._context,
                                                 data_name=CHROMA_PICTURE_DB_NAME, 
                                                 config=self._config)
    
    @timing
    def run(self):

        # exrtract data from dbeaver
        collection_infos = self.chroma_collection.collection.get(include=['embeddings', "metadatas"], limit=100000)
        df_desc = pd.DataFrame(collection_infos["ids"], columns=[self.name.id_unique])
        self.embeddings = collection_infos['embeddings']
        df_desc[self.name.cluster_id] = 0
        df_desc["batch"]=0
        df_desc["pict_path"] = [x["pict_path"] for x in collection_infos['metadatas']]

        for i in range(100000//35000 + 1):
            print(i)
            # cluster it all
            df_desc.iloc[i*35000:min((i+1)*35000, 100000), 1] = self.step_cluster.hdbscan_clustering(self.embeddings[i*35000:min((i+1)*35000, 100000)])
            df_desc.iloc[i*35000:min((i+1)*35000, 100000), 2] = i

        df_desc = df_desc.loc[df_desc["label"] != -1]
        df_desc[self.name.cluster_id] = df_desc[self.name.cluster_id].astype(str) + "_" + df_desc["batch"].astype(str)

        if self.save_pictures:
            self.save_clustered_pictures(df_desc)
            
        if self.params["verbose"] ==1:
            plot_reduced_embedding = self.step_embedding.embedding_reduction(self.embeddings, 
                                                                             method_dim_reduction="tsne")
            df_desc["x"], df_desc["y"] = zip(*plot_reduced_embedding)
            self.step_cluster.plot_clusters(df_desc)


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
            copy_picture(row["pict_path"], row["TO"])
