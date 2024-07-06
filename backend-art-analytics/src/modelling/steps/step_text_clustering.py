from typing import Dict
import pandas as pd 
from typing import List

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.Clustering import TopicClustering
from src.modelling.transformers.Embedding import StepEmbedding
from src.modelling.transformers.NlpToolBox import NLPToolBox
from src.utils.dataset_retreival import DatasetRetreiver

from src.utils.utils_crawler import copy_picture

from omegaconf import DictConfig

class StepTextClustering(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 save_embeddings : bool = False,
                 do_clustering: bool = False):

        super().__init__(context=context, config=config)

        self.save_pictures = True
        self.save_embeddings = save_embeddings
        self.to_cluster = do_clustering
        
        self.params = self._config.embedding.clustering.params
        self.prompt_name = self._config.embedding.prompt_name
        self.n_words_cluster = self.params.n_words_cluster

        self.nlp = NLPToolBox()
        self.step_cluster = TopicClustering(params=self.params)
        self.step_embedding = StepEmbedding(context=context, config=config, 
                                            type="text")
        self.data_retreiver = DatasetRetreiver(context=context, config=config)
        
    @timing
    def run(self, data_name : str, vector : str):

        #exrtract data from dbeaver
        self.vector = self.name.total_description
        data_name = self._config.cleaning.full_data_auction_houses
        df_desc =  self.data_retreiver.get_all_pictures(data_name=data_name)
        df_desc = df_desc.sample(frac=0.1)

        # create text embedding
        self.embeddings = self.step_embedding.get_text_embedding(df_desc[self.vector].tolist(), 
                                                                 prompt_name=self.prompt_name)
        
        if self.to_cluster:
            self.reduced_embedding = self.step_cluster.embedding_reduction(self.embeddings, 
                                                                            method_dim_reduction="umap")

            # get cluster 
            df_desc[self.name.cluster_id] = self.step_cluster.hdbscan_clustering(self.reduced_embedding)

            # get top 5 words of each clsuter 
            df_desc[self.name.cluster_top_words] = self.get_top_words_cluster(df_desc)

            if self.save_pictures:
                self.save_pictures_for_test()

            if self.params["verbose"] ==1:
                self.plot_2d_embeddings(df_desc)

        return df_desc 
    

    def plot_2d_embeddings(self, df_desc):
        plot_reduced_embedding = self.step_cluster.embedding_reduction(self.embeddings, 
                                                                    method_dim_reduction="tsne")
        df_desc["x"], df_desc["y"] = zip(*plot_reduced_embedding)
        self.step_cluster.plot_clusters(df_desc)


    def save_pictures_for_test(self):
        sub_df = sub_df.loc[sub_df[self.name.cluster_id] != -1]
        sub_df["TO"] = sub_df[self.name.cluster_id].apply(lambda x : "D:/data/other/" + "vase_" + str(x))
        for row in sub_df.to_dict(orient="records"):
            copy_picture(row["PICTURES"], row["TO"])

    def get_top_words_cluster(self, df_desc):
        liste_docs = df_desc[[self.name.cluster_id, self.vector]].groupby(self.name.cluster_id)[self.vector].apply(lambda x : " ".join(x))
        self.mapping_words_cluster = self.nlp.extract_words_per_cluster(liste_docs, ngram_range=(1,2), n_top_words=self.n_words_cluster)
        return df_desc[self.name.cluster_id].map(self.mapping_words_cluster)
    