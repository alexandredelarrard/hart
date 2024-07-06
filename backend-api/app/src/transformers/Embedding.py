from typing import List
import io
from PIL import Image

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.utils.utils_crawler import read_json
from src.transformers.PictureModel import PictureModel
from src.transformers.TextModel import TextModel
from omegaconf import DictConfig

from src.constants.variables import (TEXT_DB_EN,
                                     TEXT_DB_FR,
                                     PICTURE_DB)

class StepEmbedding(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 type : List[str] = [TEXT_DB_EN, TEXT_DB_FR, PICTURE_DB]):

        super().__init__(context=context, config=config)

        self.params = self._config.embedding.dim_reduc.params
        self.prompt_name = self._config.embedding.prompt_name
        self.prompt = self._config.embedding.prompt
        self.default_picture_path = self._config.picture_classification.default_image_path
        self.init_models(type)

    def init_models(self, type):

        self.models = {}

        for model_type in type:
            if model_type == TEXT_DB_EN or model_type == TEXT_DB_FR:
                self.text_batch_size = self._config.embedding.text.batch_size
                
                self.text_embedding_cls = TextModel(context=self._context, 
                                                    config=self._config,
                                                    prompt=self.prompt)
                self.models[model_type] = self.text_embedding_cls.load_model(
                                model_name = self._config.embedding.text_model[model_type]
                            )
                
            elif model_type == PICTURE_DB:
                self.fine_tuned_model =self._config.embedding.picture_model

                # get and shape data to pytorc
                self.classes_2id = read_json(path=self.fine_tuned_model + "/classes_2id.json")

                # fit model 
                self.picture_embedding_cls = PictureModel(context=self._context, config=self._config,
                                                model_name=self._config.picture_classification.model,
                                                batch_size=self._config.embedding.picture.batch_size,
                                                device=self._config.embedding.device,
                                                classes=self.classes_2id,
                                                model_path=self.fine_tuned_model)
                self.picture_embedding_cls.load_trained_model(model_path=self.fine_tuned_model)
            else:
                raise Exception("Can only handle text or picture so far. No Audio & co as embeddings")

    @timing
    def get_text_embedding(self, language_db, query_text):

        if isinstance(query_text, str):
            query_text = [query_text]

        elif isinstance(query_text, List):
            query_text = query_text

        else:
            raise Exception(f"Text need to be str or List[str] to be embedded intead of {query_text.dtype}")

        embedding = self.text_embedding_cls.embed_one_text(self.models[language_db], 
                                                           prompt_name=language_db, 
                                                           text=query_text)
        return embedding
    
    @timing
    def get_fast_picture_embedding(self, image):
        image = Image.open(io.BytesIO(image)).convert('RGB')
        return self.picture_embedding_cls.one_embedding_on_the_fly(image)
    