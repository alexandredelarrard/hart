import numpy as np
from typing import List

from tqdm import tqdm
import PIL
from PIL import Image
from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from sentence_transformers import SentenceTransformer

from src.utils.utils_crawler import read_json
from src.modelling.transformers.PictureModel import PictureModel, ArtDataset

import torch 
import torchvision.transforms as T

from omegaconf import DictConfig

class StepEmbedding(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 type : str = "text"):

        super().__init__(context=context, config=config)
        self.params = self._config.embedding.dim_reduc.params
        self.default_picture_path = self._config.picture_classification.default_picture_path
        
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

        pict_transformer = self.picture_model.load_trained_model(model_path=self.fine_tuned_model)
        test_dataset = ArtDataset(images,
                                 self.classes_2id, 
                                 transform=pict_transformer,
                                 mode="test",
                                 default_path=self.default_picture_path)
        
        candidate_subset_emb = self.picture_model.predict_embedding(test_dataset)
        
        return np.concatenate(candidate_subset_emb)
    
    @timing
    def loop_manually_per_batch(self, images : List[str]):
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
    
    def get_text_embedding(self, query_text, prompt_name):

        if isinstance(query_text, str):
            query_text = [query_text]

        elif isinstance(query_text, List):
            query_text = query_text

        else:
            raise Exception(f"Text need to be str or List[str] to be embedded intead of {query_text.dtype}")

        query_embedded = self.get_text_embeddings(query_text, 
                                                prompt_name=prompt_name)
        return query_embedded