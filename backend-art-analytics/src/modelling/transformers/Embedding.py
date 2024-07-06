import numpy as np
from typing import List

import io
from PIL import Image
from src.context import Context
from src.utils.step import Step
import torch
from src.utils.timing import timing


from src.utils.utils_crawler import read_json
from src.modelling.transformers.PictureModel import PictureModel, ArtDataset
from src.modelling.transformers.TextModel import TextModel
from src.constants.variables import (PICTURE_TYPE,
                                    TEXT_TYPE_FR, 
                                    TEXT_TYPE_EN)

from omegaconf import DictConfig

class StepEmbedding(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 type : str = "picture"):

        super().__init__(context=context, config=config)

        self.params = self._config.embedding.dim_reduc.params
        self.default_picture_path = self._config.picture_classification.default_image_path
        self.type = type
        
        if type in [TEXT_TYPE_FR, TEXT_TYPE_EN]:
            self.text_batch_size = self._config.embedding.text.batch_size
            
            self.prompt = {}
            for k, v in self._config.embedding.prompt.items():
                self.prompt[k] = v

            self.text_model = TextModel(context=self._context, 
                                        config=self._config,
                                        model_name=self._config.embedding.text_model[type],
                                        prompt=self.prompt,
                                        text_type=self.type)
            self.text_model.load_model()
            
        elif type == PICTURE_TYPE:
            
            self.fine_tuned_model =self._config.embedding.picture_model

            # get and shape data to pytorc
            self.classes_2id = read_json(path=self.fine_tuned_model + "/classes_2id.json")

            # fit model 
            self.picture_model = PictureModel(context=self._context, 
                                            config=self._config,
                                            model_name=self._config.picture_classification.model,
                                            classes=self.classes_2id,
                                            model_path=self.fine_tuned_model)
            self.picture_model.load_trained_model(model_path=self.fine_tuned_model)
            
        else:
            raise Exception(f"Can only handle text_en, text_fr or picture so far. No Audio & co as embeddings. value is {type}")
        
    def get_embeddings(self, input_list : List):
        results = {}
        if self.type in [TEXT_TYPE_FR, TEXT_TYPE_EN]:
            results[self.type] = self.get_text_embedding(input_list)
        
        elif self.type == PICTURE_TYPE:
            results[self.type] = self.get_batched_picture_embeddings(input_list)
        
        else: 
            raise Exception("Can only have values picture, text_en and text_fr")
            
        return results
    
    @timing
    def get_batched_picture_embeddings(self, images : List[str]):
        
        test_dataset = ArtDataset(images,
                                 self.classes_2id, 
                                 transform=self.picture_model.pict_transformer,
                                 mode="test",
                                 default_path=self.default_picture_path)
        
        candidate_subset_emb = self.picture_model.predict_embedding(test_dataset)
        
        return np.concatenate(candidate_subset_emb)
    
    def get_fast_picture_embedding(self, image):
        image = Image.open(io.BytesIO(image)).convert('RGB')
        return self.picture_model.one_embedding_on_the_fly(image)
    
    def get_picture_embedding(self, picture_path):
         
        if isinstance(picture_path, str):
            picture_path = [picture_path]

        elif isinstance(picture_path, List):
            picture_path = picture_path

        else:
            raise Exception(f"Text need to be str or List[str] to be embedded intead of {picture_path.dtype}")

        return self.get_batched_picture_embeddings(picture_path)
    
    def get_text_embedding(self, query_text):

        if isinstance(query_text, str):
            query_text = [query_text]

        elif isinstance(query_text, List):
            query_text = query_text

        else:
            raise Exception(f"Text need to be str or List[str] to be embedded intead of {query_text.dtype}")

        return self.text_model.embed_texts(query_text)