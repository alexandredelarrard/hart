from typing import Dict
from pathlib import Path
from torch.utils.data import Dataset
import logging

import timm
import torch
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
from PIL import Image
import peft

from src.context import Context
from src.utils.step import Step
from omegaconf import DictConfig

class ArtDataset(Dataset):

    def __init__(self, image_paths, classes, transform=None, mode: str=None, default_path:str=None):
        
        super().__init__()

        self.image_paths = image_paths
        self.transform = transform
        self.classes_2id = classes
        self.mode = mode
        self.default_image_path = default_path
        
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):

        image_filepath = self.image_paths[idx]

        try:
            image = Image.open(image_filepath).convert('RGB')
        except Exception:
            image = Image.open(self.default_image_path).convert('RGB')
            logging.error(image_filepath)

        if self.mode!="test":
            label = self.classes_2id[str(Path(image_filepath).parent).split("\\")[-1]]
        else:
            label=""

        if self.transform is not None:
            try:
                image = self.transform(image)
            except Exception:
                image = Image.open(self.default_image_path).convert('RGB')
                image = self.transform(image)
                logging.error(image_filepath)

        return {"image": image, "labels": label}
    

class PictureModel(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 model_name : str,
                 model_path : str = None,
                 batch_size : int = 32,
                 device : str = None,
                 epochs : int = 10,
                 classes : Dict = {}):

        super().__init__(context=context, config=config)

        self.model_name = model_name
        self.top_k = 5
        self.epochs = epochs
        self.batch_size=batch_size
        self.model_path = model_path

        if not self.model_name and not self.model_path:
            raise Exception("Either model name or model path should be given")

        if len(classes) == 0:
            raise Exception("You need to provide a mapping dictionnary with Ids / label mapping")

        # get classes
        self.classes_2id = classes
        self.id2_classes = {v: k for k,v in self.classes_2id.items()}
        self.num_classes = len(classes)
        self.batching = {}

        # model params
        if not device:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device

    def one_embedding_on_the_fly(self, image):
        image = self.pict_transformer(image).unsqueeze(0)
        xb = image.to(self.device)
        with torch.no_grad():
            outputs = self.new_model.forward_features(xb)
            last = self.new_model.forward_head(outputs, pre_logits=True)
        return last.cpu().numpy()

    def define_model_transformer(self, is_training : bool =True):
        self.model = timm.create_model(self.model_name, pretrained=True, num_classes=self.num_classes)
        data_config = resolve_data_config(self.model.pretrained_cfg, model=self.model)
        return create_transform(**data_config, is_training=is_training)

    def load_trained_model(self, model_path):
        self.base_model = timm.create_model(self.model_name, pretrained=True, num_classes=self.num_classes)
        self.new_model = peft.PeftModel.from_pretrained(self.base_model, model_path)
        self.data_config = resolve_data_config(self.new_model.pretrained_cfg, model=self.new_model)
        self.pict_transformer = create_transform(**self.data_config)
        self.new_model.to(self.device).eval()
