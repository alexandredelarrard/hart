from sklearn import preprocessing
import numpy as np
from typing import List
import umap.umap_ as umap
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from sentence_transformers import SentenceTransformer

from omegaconf import DictConfig


class StepEmbedding(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 database_name : str = None):

        super().__init__(context=context, config=config)

        self.prompt = {}
        for k, v in self._config.embedding[database_name].prompt.items():
            self.prompt[k] = v

        self.params = self._config.embedding[database_name].dim_reduc.params
        self.model = SentenceTransformer(self._config.embedding[database_name].model,
                                        prompts=self.prompt,
                                        device=self._config.embedding[database_name].device)

    def get_embeddings(self, input_texts : List, prompt_name):
        if prompt_name not in self.prompt.keys():
            raise Exception(f"prompt name is not part of possible prompts from config which are : \n \
                            {self.prompt.keys()}")

        return self.model.encode(input_texts, 
                                #  convert_to_tensor=True, 
                                 normalize_embeddings=True,
                                 prompt_name=prompt_name)
    
    def get_similarities(self, embeddings):
        return (embeddings @ embeddings.T) * 100
    
    def embedding_reduction(self, embeddings : np.array, 
                            method_dim_reduction : str) -> np.array:

        # PCA : reduce embeddings dim 
        if method_dim_reduction == "pca":
            self._log.info("PCA")
            new_embeddings = self.reduce_embeddings_pca(embeddings)

        # UMAP : reduce dimmension based on kullback lieber distance 
        elif method_dim_reduction == "umap":    
            self._log.info("UMAP EMBEDDING")
            new_embeddings = self.reduce_embeddings_umap(embeddings)

        # UMAP : reduce dimmension based on kullback lieber distance 
        elif method_dim_reduction == "tsne":    
            self._log.info("TSNE EMBEDDING")
            new_embeddings = self.reduce_embeddings_tsne(embeddings)
        
        else:
            raise Exception("Only PCA and UMAP available for now")

        return new_embeddings

    def reduce_embeddings_pca(self, embeddings : np.array) -> np.array:
        """
        Reduction of embedding dimension with PCA keeping 90% of info

        Returns:
            [Array]: [embeddings]
        """

        # normalize embeddings before pca
        scaler = preprocessing.StandardScaler()
        scaled_embeddings = scaler.fit_transform(embeddings)
        
        #first PCA -> keeps 95% information
        pca = PCA(random_state=42, n_components=0.95)
        af = pca.fit(scaled_embeddings)

        new_embeddings = af.transform(scaled_embeddings)
        return new_embeddings


    def reduce_embeddings_umap(self, embeddings : np.array) -> np.array:
        """
        Reduction of embedding dimension with UMAP 

        Returns:
            [Array]: [embeddings]
        """

        if len(embeddings.shape) == 2:
            umap_embeddings = umap.UMAP(random_state=42,
                                        n_neighbors=self.params["umap_n_neighbors"], 
                                        n_components=self.params["umap_n_components"], 
                                        metric='cosine').fit_transform(embeddings)
        else:
            raise Exception("Embedding should have a 2 shaped matrix")

        return umap_embeddings
    

    def reduce_embeddings_tsne(self, embeddings : np.array) -> np.array:
        """
        Reduction of embedding dimension with UMAP 

        Returns:
            [Array]: [embeddings]
        """

        if len(embeddings.shape) == 2:
            tsne_embeddings = TSNE().fit_transform(embeddings)
        else:
            raise Exception("Embedding should have a 2 shaped matrix")

        return tsne_embeddings