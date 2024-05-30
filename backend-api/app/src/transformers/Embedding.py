import numpy as np
from typing import List
import logging
import io
from PIL import Image

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from sentence_transformers import SentenceTransformer

from src.utils.utils_crawler import read_json
from src.transformers.PictureModel import PictureModel, ArtDataset
from omegaconf import DictConfig
import torch
import torchvision.transforms as T

class StepEmbedding(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 type : str = "text"):

        super().__init__(context=context, config=config)
        self.params = self._config.embedding.dim_reduc.params
        self.default_picture_path = self._config.picture_classification.default_image_path
        
        if type == "text":
            self.batch_size = self._config.embedding.text.batch_size
            
            self.prompt = {}
            for k, v in self._config.embedding.prompt.items():
                self.prompt[k] = v

            self.model = SentenceTransformer(self._config.embedding.text_model,
                                            prompts=self.prompt,
                                            device=self._config.embedding.device)
            
        elif type=="picture":
            self.batch_size = self._config.embedding.picture.batch_size
            self.fine_tuned_model =self._config.embedding.picture_model

            # get and shape data to pytorc
            self.classes_2id = read_json(path=self.fine_tuned_model + "/classes_2id.json")

            # fit model 
            self.picture_model = PictureModel(context=self._context, config=self._config,
                                            model_name=self._config.picture_classification.model,
                                            batch_size=self._config.embedding.picture.batch_size,
                                            device=self._config.embedding.device,
                                            classes=self.classes_2id,
                                            model_path=self.fine_tuned_model)
            self.picture_model.load_trained_model(model_path=self.fine_tuned_model)
        else:
            raise Exception("Can only handle TEXT or PICTURE so far. No Audio & co as embeddings")


    def get_text_embeddings(self, input_texts : List, prompt_name : str):
        if prompt_name not in self.prompt.keys():
            raise Exception(f"prompt name is not part of possible prompts from config which are : \n \
                            {self.prompt.keys()}")

        return self.model.encode(input_texts, 
                                 batch_size=self.batch_size,
                                 normalize_embeddings=False,
                                 prompt_name=prompt_name)
    
    @timing
    def get_batched_picture_embeddings(self, images : List[str]):
        
        test_dataset = ArtDataset(images,
                                 self.classes_2id, 
                                 transform=self.pict_transformer,
                                 mode="test",
                                 default_path=self.default_picture_path)
        
        candidate_subset_emb = self.picture_model.predict_embedding(test_dataset)
        
        return np.concatenate(candidate_subset_emb)
    
    def text_to_embedding(self, query_text):

        if isinstance(query_text, str):
            query_text = [query_text]

        elif isinstance(query_text, List):
            query_text = query_text

        else:
            raise Exception(f"Text need to be str or List[str] to be embedded intead of {query_text.dtype}")

        query_embedded = self.get_text_embeddings(query_text, 
                                                prompt_name=self.prompt_name)
        return query_embedded
    
    def read_images(self, images : List[str]):

        pils_images= []
        for image in images:
            if isinstance(image, str):
                try:
                    pils_images.append(Image.open(image).convert("RGB"))
                except Exception:
                    self._log.error(f"No picture avaiable for {image} path. FILL with picture MISSING.jpg")
                    pils_images.append(Image.open(self.default_picture_path))

            else:
                raise Exception("Images must be passed as string path to \
                                the file for read to embed them")
        return pils_images
    
    def get_picture_embedding(self, picture_path):
         
        if isinstance(picture_path, str):
            picture_path = [picture_path]

        elif isinstance(picture_path, List):
            picture_path = picture_path

        else:
            raise Exception(f"Text need to be str or List[str] to be embedded intead of {picture_path.dtype}")

        return self.get_batched_picture_embeddings(picture_path)
    
    def get_fast_picture_embedding(self, image):
        image = Image.open(io.BytesIO(image))
        return self.picture_model.one_embedding_on_the_fly(image)
    
    def get_text_embedding(self, query_text, prompt_name):

        if isinstance(query_text, str):
            query_text = [query_text]

        elif isinstance(query_text, List):
            query_text = query_text

        else:
            raise Exception(f"Text need to be str or List[str] to be embedded intead of {query_text.dtype}")

        return self.get_text_embeddings(query_text, prompt_name=prompt_name)