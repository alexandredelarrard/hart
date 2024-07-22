import numpy as np
from typing import List
from pathlib import Path
import io
from PIL import Image

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.utils.utils_crawler import read_json

from src.modelling.transformers.PictureModel import PictureModel, ArtDataset
from src.modelling.transformers.TextModel import TextModel
from src.constants.variables import PICTURE_DB, TEXT_DB_FR, TEXT_DB_EN

from omegaconf import DictConfig


class StepEmbedding(Step):

    def __init__(
        self,
        context: Context,
        config: DictConfig,
        type: List[str] = [TEXT_DB_EN, TEXT_DB_FR, PICTURE_DB],
    ):

        super().__init__(context=context, config=config)

        self.params = self._config.embedding.dim_reduc.params
        self.prompt_name = self._config.embedding.prompt_name
        self.prompt = self._config.embedding.prompt
        self.default_picture_path = self._context.paths["DEFAULT"] / Path(
            self._config.picture_classification.default_image_path
        )
        self.fine_tuned_model_name = self._context.paths["MODEL"] / Path(
            self._config.embedding.picture_model_path
        )

        self.init_models(type)

    def init_models(self, type: List[str]):

        self.models = {}

        for model_type in type:
            if model_type == TEXT_DB_EN or model_type == TEXT_DB_FR:
                self.text_batch_size = self._config.embedding.text.batch_size

                self.prompt = {}
                for k, v in self._config.embedding.prompt.items():
                    self.prompt[k] = v

                self.text_embedding_cls = TextModel(
                    context=self._context, config=self._config, prompt=self.prompt
                )
                self.models[model_type] = self.text_embedding_cls.load_model(
                    model_name=self._config.embedding.text_model[model_type]
                )

            elif model_type == PICTURE_DB:

                # get and shape data to pytorc
                self.classes_2id = read_json(
                    path=self.fine_tuned_model_name / Path("classes_2id.json")
                )

                # fit model
                self.picture_model = PictureModel(
                    context=self._context,
                    config=self._config,
                    model_name=self._config.picture_classification.model,
                    classes=self.classes_2id,
                    model_path=self.fine_tuned_model_name,
                )
                self.picture_model.load_trained_model(
                    model_path=self.fine_tuned_model_name
                )

            else:
                raise Exception(
                    f"Can only handle text or picture so far. No Audio & co as embeddings. value is {type}"
                )

    @timing
    def get_batched_picture_embeddings(self, images: List[str]):

        test_dataset = ArtDataset(
            images,
            self.classes_2id,
            transform=self.picture_model.pict_transformer,
            mode="test",
            default_path=self.default_picture_path,
        )

        candidate_subset_emb = self.picture_model.predict_embedding(test_dataset)

        return np.concatenate(candidate_subset_emb)

    @timing
    def get_fast_picture_embedding(self, image):
        image = Image.open(io.BytesIO(image)).convert("RGB")
        return self.picture_model.one_embedding_on_the_fly(image)

    @timing
    def get_batched_text_embeddings(self, language_db, query_text):

        if isinstance(query_text, str):
            query_text = [query_text]

        elif isinstance(query_text, List):
            query_text = query_text

        else:
            raise Exception(
                f"Text need to be str or List[str] to be embedded intead of {query_text.dtype}"
            )

        embedding = self.text_embedding_cls.embed_texts(
            model=self.models[language_db], prompt_name=language_db, texts=query_text
        )
        return embedding

    @timing
    def get_fast_text_embedding(self, language_db, query_text):

        if isinstance(query_text, str):
            query_text = [query_text]

        elif isinstance(query_text, List):
            query_text = query_text

        else:
            raise Exception(
                f"Text need to be str or List[str] to be embedded intead of {query_text.dtype}"
            )

        embedding = self.text_embedding_cls.embed_one_text(
            self.models[language_db], prompt_name=language_db, text=query_text
        )
        return embedding
