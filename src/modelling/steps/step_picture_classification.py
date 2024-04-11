import glob
import os 
import random
import numpy as np
import shutil
import swifter
from datetime import datetime

from tqdm import tqdm 
import matplotlib.pyplot as plt
from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from src.utils.utils_crawler import (read_json,
                                     save_json)
from src.modelling.transformers.PictureModel import PictureModel, ArtDataset

from omegaconf import DictConfig


class StepPictureClassification(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 save_model : bool = True):

        super().__init__(context=context, config=config)

        self.ratio_validation = self._config.picture_classification.ratio_validation
        self.model_name = self._config.picture_classification.model
        self.picture_path = self._config.picture_classification.pictures_path
        self.train_batch_size = self._config.picture_classification.train_batch_size
        self.test_batch_size = self._config.picture_classification.test_batch_size
        self.device = self._config.picture_classification.device
        self.fine_tuned_model=self._config.picture_classification.fine_tuned_model
        self.epochs = self._config.picture_classification.epochs
        self.default_image_path= self._config.picture_classification.default_image_path
        self.full_data = self._config.cleaning.full_data_auction_houses

        self.save_model = save_model
        self.today = datetime.today().strftime("%d_%m_%Y")


    @timing
    def training(self):

        # get and shape data to pytorc
        self.classes_2id = self.define_num_classes()

        # fit model 
        picture_model = PictureModel(context=self._context, config=self._config,
                                     model_name=self.model_name,
                                     batch_size=self.train_batch_size,
                                     device=self.device,
                                     classes=self.classes_2id,
                                     epochs=self.epochs)

        pict_transformer = picture_model.define_model_transformer()

        # data defined and shaped
        self.data = self.get_train_test_data(ratio_validation=self.ratio_validation)
        train_dataset = ArtDataset(self.data["train"], self.classes_2id, transform=pict_transformer,
                                 default_path=self.default_image_path)
        validation_dataset = ArtDataset(self.data["validation"], self.classes_2id, transform=pict_transformer,
                                 default_path=self.default_image_path)
        
        picture_model.fit(train_dataset, validation_dataset)

        if self.save_model:
            picture_model.save_model(self.fine_tuned_model)
            save_json(self.classes_2id, 
                      path=self.fine_tuned_model + "/classes_2id.json")
        
        return picture_model


    @timing
    def predicting(self, view_name="TEST_0.05_06_04_2024"):

        #get data
        df = self.read_sql_data(self.full_data)
        df_done = self.read_sql_data(view_name)

        # ensure pictures available and subsample
        df = self.clean_list_pictures(df, df_done)
        df = df.sample(frac=0.06)

        # get and shape data to pytorc
        self.classes_2id = read_json(path=self.fine_tuned_model + "/classes_2id.json")

        # fit model 
        picture_model = PictureModel(context=self._context, config=self._config,
                                     model_name=self.model_name,
                                     batch_size=self.test_batch_size,
                                     device=self.device,
                                     classes=self.classes_2id,
                                     model_path=self.fine_tuned_model)
        
        pict_transformer = picture_model.load_trained_model(model_path=self.fine_tuned_model)
        test_dataset = ArtDataset(df["from"].tolist(),
                                 self.classes_2id, 
                                 transform=pict_transformer,
                                 mode="test",
                                 default_path=self.default_image_path)

        # predict
        answers = picture_model.predict(test_dataset)

        # shape and save predictions
        answers = self.shape_answer(answers, picture_model.id2_classes)
        answers["PICTURES"] = df["from"].tolist()
        answers["ID_ITEM"] = df["ID_ITEM"].tolist()
        answers['TOTAL_DESCRIPTION'] = df['TOTAL_DESCRIPTION'].tolist()

        self.write_sql_data(dataframe=answers,
                            table_name=view_name + "_" + self.today,
                            if_exists="append")
        
        return answers
    

    def clean_list_pictures(self, df, df_done):

        df["from"] = df[[self.name.seller, 
                         self.name.id_picture]].apply(lambda x: 
                                                      f"D:/data/{x['SELLER']}/pictures/{x['ID_PICTURE']}.jpg", 
                                                      axis=1)
        df = df.loc[df["ID_PICTURE"].notnull()]

        df["EXISTS_PICT"] = df["from"].swifter.apply(lambda x : os.path.isfile(x))
        df = df[df["EXISTS_PICT"]].reset_index(drop=True)

        df = df.loc[~df[self.name.id_item].isin(df_done[self.name.id_item].tolist())]

        return df

    
    def save_pictures_to_folders(self, answers):

        sub_answers = answers.loc[answers["TOP_0"].isin(["cle"])]
        sub_answers = sub_answers.loc[sub_answers["PROBA_0"] >=0.85]
        sub_answers["save_path"] = sub_answers["TOP_0"].apply(lambda x : self.picture_path + f"{x}")

        for row in tqdm(sub_answers.to_dict(orient="records")):
            try:
                shutil.move(row["PICTURES"], row["save_path"])
            except Exception as e:
                self._log.warning(e)        
    

    def plot_results(self, answers):
        for row in answers.to_dict(orient="records"):
            img = plt.imread(row["PICTURES"])
            plt.imshow(img)
            plt.title(row["TOP_0"] + " " + str(row["PROBA_0"]))
            plt.show()

        return answers
    

    def define_num_classes(self):

        folders = [os.path.basename(x[0]) for x in os.walk(self.picture_path)]
        folders = list(set(folders) - set([""]))

        self.classes_2id = {}
        for i, classe in enumerate(np.sort(folders)):
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

    def shape_answer(self, answers, id2_classes):
        for col in [x for x in answers.columns if "TOP" in x]:
            answers[col] = answers[col].map(id2_classes)
        return answers
