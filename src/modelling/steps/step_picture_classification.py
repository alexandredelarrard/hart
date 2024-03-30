import glob
import os 
import random
import numpy as np
import shutil

from tqdm import tqdm 
import matplotlib.pyplot as plt
from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from src.modelling.transformers.PictureModel import PictureModel, ArtDataset

from omegaconf import DictConfig


class StepPictureClassification(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 database_name : str = "drouot",
                 save_model : bool = True):

        super().__init__(context=context, config=config)

        self.database_name = database_name

        self.ratio_validation = self._config.picture_classification.ratio_validation
        self.model_name = self._config.picture_classification.model
        self.picture_path = self._config.picture_classification.pictures_path
        self.batch_size = self._config.picture_classification.batch_size
        self.device = self._config.picture_classification.device
        self.fine_tuned_model=self._config.picture_classification.fine_tuned_model
        self.save_model = save_model

        self.sql_table_name = self._config.embedding[database_name].origine_table_name

    @timing
    def training(self):

        # get and shape data to pytorc
        self.classes_2id = self.define_num_classes()

        # fit model 
        picture_model = PictureModel(context=self._context, config=self._config,
                                     model_name=self.model_name,
                                     batch_size=self.batch_size,
                                     device=self.device,
                                     classes=self.classes_2id,
                                     epochs=10)

        pict_transformer = picture_model.define_model_transformer()

        # data defined and shaped
        self.data = self.get_train_test_data(ratio_validation=self.ratio_validation)
        train_dataset = ArtDataset(self.data["train"], self.classes_2id, transform=pict_transformer)
        validation_dataset = ArtDataset(self.data["validation"], self.classes_2id, transform=pict_transformer)
        
        picture_model.fit(train_dataset, validation_dataset)

        if self.save_model:
            picture_model.save_model(self.fine_tuned_model)
        
        return picture_model


    @timing
    def predicting(self, liste_pictures):

        liste_pictures = glob.glob("./data/drouot/pictures_old/*.jpg")[:10000]

        # get and shape data to pytorc
        self.classes_2id = self.define_num_classes()

        # fit model 
        picture_model = PictureModel(context=self._context, config=self._config,
                                     model_name=self.model_name,
                                     batch_size=self.batch_size,
                                     device=self.device,
                                     classes=self.classes_2id,
                                     model_path=self.fine_tuned_model)
        
        pict_transformer = picture_model.load_trained_model(model_path=self.fine_tuned_model)
        test_dataset = ArtDataset(liste_pictures,
                                 self.classes_2id, 
                                 transform=pict_transformer,
                                 mode="test")

        # predict
        answers = picture_model.predict(test_dataset)
        answers = self.shape_answer(answers, picture_model.id2_classes)
        answers["PICTURES"] = liste_pictures

        # plot or not 
        # self.plot_results(answers.iloc[-10:])

        return answers
    
    def save_pictures_to_folders(self, answers):

        answers = answers.loc[answers["TOP_0"].isin(["miroir", "arme feu", "arme blanche", "boucle oreille",
                                                     "stylo", "foulard", "cle", "canape", "ceinture", "chaussures",
                                                     "chaise", "sac", "evantail", "musique", "robe", "broche", "collier",
                                                     "bague", "applique"])]
        answers = answers.loc[answers["PROBA_0"] >=0.5]
        answers["save_path"] = answers["TOP_0"].apply(lambda x :  self.picture_path + f"{x}")

        for row in tqdm(answers.to_dict(orient="records")):
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
