import os 
from tqdm import tqdm
from typing import Dict
from pathlib import Path
from torch.utils.data import Dataset
import pandas as pd 
import logging
import numpy as np

import timm
import torch
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
from PIL import Image
import peft

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

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
        target_modules = ['blocks.23.mlp.fc2', 'blocks.23.mlp.fc1'] #r"blocks.23.*\.mlp\.fc\d" # , 'blocks.22.mlp.fc2', 'blocks.23.mlp.fc1'
        self.criterion = torch.nn.CrossEntropyLoss()
        self.lora_model_config = peft.LoraConfig(r=8, target_modules=target_modules, modules_to_save=["head"])

        if not device:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device

    def fit(self, train_dataset : Dataset, val_dataset : Dataset = None):

        # batching data
        self.batching_data(train_dataset, mode="train")
        if isinstance(val_dataset, Dataset):
            self.batching_data(val_dataset, mode="validation")

        # train model 
        self.peft_model = peft.get_peft_model(self.model, self.lora_model_config).to(self.device)
        self.optimizer = torch.optim.Adam(self.peft_model.parameters(), lr=2e-4)
        self.peft_model.print_trainable_parameters()

        # iterate per epoch
        for epoch in range(self.epochs):
            train_loss = self.train_epoch(train_data = self.batching["train"])
            train_loss_total = self.evaluate(train_loss, mode="train")
            to_print = f"{epoch=:<2}  {train_loss_total=:.4f}"

            if isinstance(val_dataset, Dataset):
                valid_loss, n_total, correct = self.evaluate_epoch(self.batching["validation"])
                valid_loss_total = self.evaluate(valid_loss, mode="validation")
                valid_acc_total = correct / n_total
                to_print += f" {valid_loss_total=:.4f} {valid_acc_total=:.4f}"

            self._log.info(to_print)
    

    def train_epoch(self, train_data):
        self.peft_model.train()
        train_loss = 0

        for batch in train_data:
            xb, yb = batch["image"], batch["labels"]
            xb, yb = xb.to(self.device), yb.to(self.device)
            outputs = self.peft_model(xb)

            lsm = torch.nn.functional.log_softmax(outputs, dim=-1)
            loss = self.criterion(lsm, yb)
            train_loss += loss.detach().float()
            loss.backward()
            self.optimizer.step()
            self.optimizer.zero_grad()
        
        return train_loss


    def evaluate_epoch(self, validation_data):

        self.peft_model.eval()
        valid_loss = 0
        correct = 0
        n_total = 0
        for batch in validation_data:
            xb, yb = batch["image"], batch["labels"]
            xb, yb = xb.to(self.device), yb.to(self.device)
            with torch.no_grad():
                outputs = self.peft_model(xb)
            lsm = torch.nn.functional.log_softmax(outputs, dim=-1)
            loss = self.criterion(lsm, yb)
            valid_loss += loss.detach().float()

            correct += (outputs.argmax(-1) == yb).sum().item()
            n_total += len(yb)
        
        return valid_loss, n_total, correct
    
    def predict(self, test_dataset : Dataset):

        self.batching_data(test_dataset, mode="test")
        self.new_model.to(self.device).eval()

        sorties = []
        for batch in tqdm(self.batching["test"]):
            xb = batch["image"]
            xb = xb.to(self.device)
            with torch.no_grad():
                outputs = self.new_model(xb)
            lsm = torch.nn.functional.softmax(outputs, dim=-1)
            answers = torch.topk(lsm, k=self.top_k)
            sorties.append(answers)

        return self.clean_sorties(sorties)
    
    def predict_embedding(self, test_dataset : Dataset):

        self.batching_data(test_dataset, mode="test")
        self.new_model.to(self.device).eval()

        sorties = []
        for batch in tqdm(self.batching["test"]):
            xb = batch["image"]
            xb = xb.to(self.device)
            with torch.no_grad():
                outputs = self.new_model(xb)
                
            self._log.info(outputs.keys())
            last = outputs.last_hidden_state.mean(1)

            sorties.append(last)
        
        return sorties

    def batching_data(self, data, mode="train"):
        self.batching[mode] = torch.utils.data.DataLoader(data, shuffle=False, batch_size=self.batch_size)
        
    def define_model_transformer(self, is_training : bool =True):
        self.model = timm.create_model(self.model_name, pretrained=True, num_classes=self.num_classes)
        data_config = resolve_data_config(self.model.pretrained_cfg, model=self.model)
        return create_transform(**data_config, is_training=is_training)

    def save_model(self, save_path):
        self.peft_model.save_pretrained(save_path)

        for file_name in os.listdir(save_path):
            file_size = os.path.getsize(save_path + "/" + file_name)
            self._log.info(f"File Name: {file_name}; File Size: {file_size / 1024:.2f}KB")

    def load_trained_model(self, model_path):
        self.base_model = timm.create_model(self.model_name, pretrained=True, num_classes=self.num_classes)
        self.new_model = peft.PeftModel.from_pretrained(self.base_model, model_path)
        data_config = resolve_data_config(self.new_model.pretrained_cfg, model=self.new_model)
        return create_transform(**data_config, is_training=False)

    def evaluate(self, loss, mode="train"):
        loss_total = (loss / len(self.batching[mode])).item()
        return loss_total

    def clean_sorties(self, sorties):

        proba_cols = [f"PROBA_{i}" for i in range(self.top_k)]
        columns = proba_cols + [f"TOP_{i}" for i in range(self.top_k)]
        total = pd.DataFrame()
        for batch in sorties:
            probas, classes = batch[0].cpu().numpy(), batch[1].cpu().numpy()
            batch_total = pd.concat([pd.DataFrame(probas), pd.DataFrame(classes)], axis=1)
            total = pd.concat([total, batch_total], axis=0)
        total.columns = columns

        return total.reset_index(drop=True)
    