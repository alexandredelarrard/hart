import glob
import os 
import random
import pandas as pd 
from pathlib import Path
from torch.utils.data import Dataset

import timm
import torch
from skimage import io
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
from PIL import Image
import matplotlib.pyplot as plt
import peft

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from omegaconf import DictConfig

class ArtDataset(Dataset):

    def __init__(self, image_paths, classes, transform=None):
        
        super().__init__()
        self.image_paths = image_paths
        self.transform = transform
        self.classes_2id = classes
        
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):

        image_filepath = self.image_paths[idx]
        image = Image.open(image_filepath)

        label = self.classes_2id[str(Path(image_filepath).parent).split("\\")[-1]]

        if self.transform is not None:
            image = self.transform(image)

        sample = {"image": image, "labels": label}

        return sample
    


class StepPictureClassification(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 database_name : str = "drouot"):

        super().__init__(context=context, config=config)

        self.database_name = database_name

        self.ratio_validation = self._config.picture_classification.ratio_validation
        self.model_name = self._config.picture_classification.model
        self.picture_path = self._config.picture_classification.pictures_path
        self.batch_size = self._config.picture_classification.batch_size
        self.device = self._config.picture_classification.device

        self.sql_table_name = self._config.embedding[database_name].origine_table_name

    @timing
    def run(self):

        # get and shape data to pytorc
        self.classes_2id = self.define_num_classes()
        self.id2_classes = {v: k for k,v in self.classes_2id.items()}

        # define model
        pict_transform = self.define_model()

        # data defined and shaped
        self.data = self.get_train_test_data(ratio_validation=self.ratio_validation)
        train_dataset = ArtDataset(self.data["train"], self.classes_2id, transform=pict_transform)
        validation_dataset = ArtDataset(self.data["validation"], self.classes_2id, transform=pict_transform)
        self.batching_data(train_dataset, validation_dataset)

        # train model 
        config = peft.LoraConfig(r=8, target_modules=r"blocks.23.*\.mlp\.fc\d", modules_to_save=["head"])
        self.peft_model = peft.get_peft_model(self.model, config).to(self.device)
        optimizer = torch.optim.Adam(self.peft_model.parameters(), lr=2e-4)
        criterion = torch.nn.CrossEntropyLoss()
        self.peft_model.print_trainable_parameters()

        self.train(optimizer, criterion, epochs=10)

    
    def define_num_classes(self):

        folders = [os.path.basename(x[0]) for x in os.walk(self.picture_path)]
        folders = list(set(folders) - set([""]))

        self.classes_2id = {}
        for i, classe in enumerate(folders):
            self.classes_2id[classe] = i

        return self.classes_2id
    
    def get_train_test_data(self, ratio_validation):

        pictures_paths = glob.glob(self.picture_path + "/*/*.jpg")

        random.shuffle(pictures_paths)
        train_volume = int(len(pictures_paths)*(1-ratio_validation))
        self._log.info(f"TRAIN DATA VOLUME = {train_volume} / VAL VOLUME = {len(pictures_paths) - train_volume}")

        data = {"train" : pictures_paths[:train_volume],
                "validation" : pictures_paths[train_volume:]}
        
        return data

    
    def define_model(self):
        self.model = timm.create_model(self.model_name, pretrained=True, num_classes=len(self.classes_2id))
        data_config = resolve_data_config(self.model.pretrained_cfg, model=self.model)
        return create_transform(**data_config)

    def process(self, batch):
        x = torch.cat([self.transform(img).unsqueeze(0) for img in batch["image"]])
        y = torch.tensor(batch["labels"])
        return {"image": x, "labels": y}
    
    def batching_data(self, train_data, val_data):
        self.train_loader = torch.utils.data.DataLoader(train_data, shuffle=True, batch_size=self.batch_size)
        self.valid_loader = torch.utils.data.DataLoader(val_data, shuffle=True, batch_size=self.batch_size)

    def predict(self, image):

        output = model(transforms(img).unsqueeze(0)) 

    
    def train(self, optimizer, criterion, epochs):

        for epoch in range(epochs):

            train_loss = self.train_epoch(optimizer, criterion)
            valid_loss, n_total, correct = self.evaluate_epoch(criterion)
            
            train_loss_total, valid_loss_total = self.evaluate(train_loss, valid_loss)
            valid_acc_total = correct / n_total

            self._log.info(f"{epoch=:<2}  {train_loss_total=:.4f}  {valid_loss_total=:.4f}  {valid_acc_total=:.4f}")


    def train_epoch(self, optimizer, criterion):
        self.peft_model.train()
        train_loss = 0

        for batch in self.train_loader:
            xb, yb = batch["image"], batch["labels"]
            xb, yb = xb.to(self.device), yb.to(self.device)
            outputs = self.model(xb)

            lsm = torch.nn.functional.log_softmax(outputs, dim=-1)
            loss = criterion(lsm, yb)
            train_loss += loss.detach().float()
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        
        return train_loss

    def evaluate_epoch(self, criterion):

        self.peft_model.eval()
        valid_loss = 0
        correct = 0
        n_total = 0
        for batch in self.valid_loader:
            xb, yb = batch["image"], batch["labels"]
            xb, yb = xb.to(self.device), yb.to(self.device)
            with torch.no_grad():
                outputs = self.model(xb)
            lsm = torch.nn.functional.log_softmax(outputs, dim=-1)
            loss = criterion(lsm, yb)
            valid_loss += loss.detach().float()
            correct += (outputs.argmax(-1) == yb).sum().item()
            n_total += len(yb)
        
        return valid_loss, n_total, correct
           
    def evaluate(self, train_loss, valid_loss):
        train_loss_total = (train_loss / len(self.train_loader)).item()
        valid_loss_total = (valid_loss / len(self.valid_loader)).item()
        return train_loss_total, valid_loss_total

        
    def save_model(self):
        peft_bert_model_path = "./data/models/peft_block23_vit_large_patch14_clip_224_280324"
        self.peft_model.save_pretrained(peft_bert_model_path)

        for file_name in os.listdir(peft_bert_model_path):
            file_size = os.path.getsize(peft_bert_model_path + "/" + file_name)
            print(f"File Name: {file_name}; File Size: {file_size / 1024:.2f}KB")

    def load_trained_model(self):
        config = peft.PeftConfig.from_pretrained("./data/models/peft_block23_vit_large_patch14_clip_224_280324")
        self.new_model = timm.create_model(self.model_name, pretrained=True, num_classes=len(self.classes_2id))
        self.new_model = peft.PeftModel.from_pretrained(self.new_model, "./data/models/peft_block23_vit_large_patch14_clip_224_280324")

    def predict(self):
        self.new_model = self.new_model.eval()

        # get model specific transforms (normalization, resize)
        data_config = timm.data.resolve_model_data_config(self.new_model )
        transforms = timm.data.create_transform(**data_config, is_training=False)

        list_picts = glob.glob(r"./data/drouot/pictures_old/*.jpg")

        random.shuffle(list_picts)

        for path in list_picts[:10]:
            img = Image.open(path)
            output = self.new_model(transforms(img).unsqueeze(0))

            answer = shape_answer(output)
            self._log.info(answer)
            plt.imshow(img)
            plt.show()
        
    def shape_answer(self, output, top_k=5):

        top5_probabilities, top5_class_indices = torch.topk(output.softmax(dim=1) * 100, k=top_k)

        classes = top5_class_indices.detach().numpy()
        probas = top5_probabilities.detach().numpy()

        final = pd.DataFrame([], index= list(range(len(probas[0]))))
        final["PROBA"] = probas[0]
        final["CLASSES"]= classes[0]
        final["CLASSES"] = final["CLASSES"].map(self.id2_classes)

        return final