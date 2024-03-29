from sklearn import preprocessing
import numpy as np
from typing import List
import umap.umap_ as umap
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from tqdm import tqdm
import PIL
from PIL import Image
from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from sentence_transformers import SentenceTransformer
# from chromadb.utils import embedding_functions
from transformers import AutoImageProcessor, Swinv2Model, AutoFeatureExtractor

import torch 
import torchvision.transforms as T

from omegaconf import DictConfig


class StepEmbedding(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 database_name : str = None,
                 type : str = "text"):

        super().__init__(context=context, config=config)
        self.params = self._config.embedding[database_name].dim_reduc.params
        self.default_picture_path = self._config.cleaning.default_picture_path
        
        if type == "text":
            self.batch_size = self._config.embedding[database_name].text.batch_size
            
            self.prompt = {}
            for k, v in self._config.embedding[database_name].text.prompt.items():
                self.prompt[k] = v

            self.model = SentenceTransformer(self._config.embedding.text_model,
                                            prompts=self.prompt,
                                            device=self._config.embedding.device)
            
        elif type=="picture":
            self.batch_size = self._config.embedding[database_name].picture.batch_size

            model_ckpt = self._config.embedding.picture_model
            self.processor = AutoImageProcessor.from_pretrained(model_ckpt)
            self.extractor = AutoFeatureExtractor.from_pretrained(model_ckpt)
            self.model = Swinv2Model.from_pretrained(model_ckpt)
            self.model.to(self._config.embedding.device)
        
        else:
            raise Exception("Can only handle TEXT or PICTURE so far. No Audio & co as embeddings")


    def get_text_embeddings(self, input_texts : List, prompt_name : str):
        if prompt_name not in self.prompt.keys():
            raise Exception(f"prompt name is not part of possible prompts from config which are : \n \
                            {self.prompt.keys()}")

        return self.model.encode(input_texts, 
                                 batch_size=self.batch_size,
                                #  convert_to_tensor=True, 
                                 normalize_embeddings=False,
                                 prompt_name=prompt_name)
    
    def get_batched_picture_embeddings(self, images : List[str]):
        
        steps = len(images) // self.batch_size 

        for i in tqdm(range(steps+1)):
            sub_images= images[i*self.batch_size:(i+1)*self.batch_size]
            pils_images = self.read_images(sub_images)
            extract = self.get_picture_embeddings(pils_images).numpy()

            if i == 0:
                candidate_subset_emb = extract
            else:
                candidate_subset_emb = np.concatenate((candidate_subset_emb, extract))

        return candidate_subset_emb
            
    @timing
    def get_picture_embeddings(self, images : List[PIL.Image]):

        # `transformation_chain` is a compostion of preprocessing
        # transformations we apply to the input images to prepare them
        # for the model.

        # normalize picture
        transformation_chain = T.Compose(
            [
                # We first resize the input image to 256x256 and then we take center crop.
                T.Resize(int((256 / 224) * self.extractor.size["height"])),
                T.CenterCrop(self.extractor.size["height"]),
                T.ToTensor(),
                T.Normalize(mean=self.extractor.image_mean, std=self.extractor.image_std),
            ]
        )
        
        image_batch_transformed = torch.stack(
            [transformation_chain(image) for image in images]
        )

        new_batch = {"pixel_values": image_batch_transformed.to(self.model.device)}
        with torch.no_grad():
            embeddings = self.model(**new_batch).last_hidden_state[:, 0].cpu()

        return embeddings
    
    def read_images(self, images : List[str]):

        pils_images= []
        for image in images:
            if isinstance(image, str):
                try:
                    pils_images.append(Image.open(image))
                except Exception:
                    self._log.error(f"No picture avaiable for {image} path. FILL with picture MISSING.jpg")
                    pils_images.append(Image.open(self.default_picture_path))

            else:
                raise Exception("Images must be passed as string path to \
                                the file for read to embed them")
        return pils_images
    
    def get_similarities(self, embeddings):
        return (embeddings @ embeddings.T) * 100
    
    @timing
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