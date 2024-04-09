import pandas as pd 
from typing import Dict
import lightgbm as lgb 
from datetime import datetime
from sklearn.model_selection import KFold

from src.constants.variables import date_format
from src.modelling.transformers.ModelEvaluator import ModelEvaluator

from src.utils.timing import timing
from src.utils.utils_crawler import (save_pickle_file,
                                    read_pickle)

class TrainLightgbmModel(ModelEvaluator):
    """
    Wrapper around LightGBM model responsible for
        * fitting the LightGBM model on in put data.
        * evaluating model performance on a tests dataset.
        * Training on the overall dataset if no test set is given

    Arguments:
        object {[type]} -- 
    """    
    
    def __init__(self, config : Dict, 
                        category : str = "vase"):

        self.today = datetime.today().strftime(date_format)
        self.random_state=config.gbm_training.seed
        self.save_model_path=config.gbm_training.save_model_path

        self.target_name = config.gbm_training[category].model_target
        self.model_features = config.gbm_training[category].model_features
        self.model_features = [x.upper() for x in self.model_features]
        self.model_parameters = config.gbm_training[category].model_parameters
        self.categorical_features = config.gbm_training[category].categorical_features

        self.n_splits=config.gbm_training[category].cross_validation.n_splits

        self.verbose = 100
        if "verbose_eval" in self.model_parameters.keys():
            self.verbose = self.model_parameters.verbose_eval
        elif "verbose" in self.model_parameters.keys():
            self.verbose = self.model_parameters.verbose

        self.weight = None
        if "model_weight" in config.gbm_training[category].keys():
            if config.gbm_training[category].model_weight:
                self.weight = config.gbm_training[category].model_weight


    @timing
    def fit(self, train_data, test_data=None, init_score=None):
        """
        Creates LightGBM model instance and trains on a train dataset. If a tests set is provided,
        we validate on this set and use early stopping to avoid over-fitting.
        """

        train_data = self.ensure_categorical(train_data)
        
        if isinstance(test_data, pd.DataFrame):

            test_data = self.ensure_categorical(test_data)

            if "early_stopping_round" not in self.model_parameters.keys():
                self.model_parameters["early_stopping_round"] = 40

            if "verbose_eval" in self.model_parameters.keys():
                self.model_parameters.pop("verbose_eval")

            if self.weight:
                train_weight = train_data[self.weight]
                test_weight  = test_data[self.weight]
            else:
                train_weight = None
                test_weight = None

            if init_score: 
                train_init_bias = train_data[init_score]
                test_init_bias = test_data[init_score]
            else:
                train_init_bias = None
                test_init_bias = None

            # model training and prediction of val
            # have an idea of the error rate and use early stopping round
            train_data = lgb.Dataset(
                train_data[self.model_features], 
                label=train_data[self.target_name], 
                weight=train_weight,
                init_score=train_init_bias,
                categorical_feature=self.categorical_features
            )

            val_data = lgb.Dataset(
                test_data[self.model_features], 
                label=test_data[self.target_name], 
                weight=test_weight,
                init_score=test_init_bias,
                categorical_feature=self.categorical_features
            )

            self.model = lgb.train(self.model_parameters,
                                    train_set=train_data, 
                                    valid_sets=[train_data, val_data],
                                    valid_names=["data_train", "data_valid"])

        else:
            if "early_stopping_round" in self.model_parameters:
                self.model_parameters.pop("early_stopping_round", None)

            if self.weight:
                sample_weight = train_data[self.weight]
            else:
                sample_weight = None

            if init_score: 
                init_bias = train_data[init_score]
            else:
                init_bias = None

            if self.model_parameters["objective"] == "binary":
                self.model = lgb.LGBMClassifier(**self.model_parameters)
            else:
                self.model = lgb.LGBMRegressor(**self.model_parameters)
            
            self.model.fit(train_data[self.model_features],
                            train_data[self.target_name], 
                            sample_weight=sample_weight,
                            init_score= init_bias,
                            categorical_feature=self.categorical_features)

    @timing
    def predict(self, test_data, init_score=None):
        """
        Takes model and tests dataset as input, computes predictions for the tests dataset, and evaluates metric
        on the predictions. Returns tests dataset with added columns for pediction and metrics.
        """

        test_data = self.ensure_categorical(test_data)
        prediction = self.model.predict(test_data[self.model_features])
        if init_score: 
            prediction = prediction + test_data[init_score]

        return prediction


    def modelling_cross_validation(self, data=None, init_score=None):
        """
        Fits model using k-fold cross-validation on a train set.
        """

        if not isinstance(data, pd.DataFrame):
            raise Exception("You need to provide a dataset to perform cross validation")
        else:
            data = data.reset_index(drop=True)

        kf = KFold(n_splits=self.n_splits,
                    random_state=self.random_state,
                    shuffle=True)

        self.total_test = pd.DataFrame()
        for train_index, val_index in kf.split(data.index, data.index):

            train_data = data.loc[train_index]
            test_data = data.loc[val_index]

            self.fit(train_data, test_data, init_score)
            x_val = self.predict(test_data, init_score)

            self.evaluate_model(self.model_parameters, 
                                y_prediction=x_val,
                                y_true=test_data[self.target_name].tolist())

            # concatenate all test_errors
            test_data["PREDICTION"] = x_val
            self.total_test = pd.concat([self.total_test, test_data], axis=0)
        
        return self.total_test.reset_index(drop=True)
    
    def ensure_categorical(self, data):
        for col in self.categorical_features:
            data[col] = data[col].astype("category")
        return data

    def save_model(self, model):
        dict_to_save= {"model": model,
                       "model_parameters": self.model_parameters,
                       "model_features": self.model_features,
                       "categorical_features": self.categorical_features}
        save_pickle_file(dict_to_save, path=self.save_model_path)


    def load_model(self):
        dict_saved = read_pickle(self.save_model_path)
        self.model = dict_saved["model"]
        self.model_parameters = dict_saved["model_parameters"]
        self.model_features = dict_saved["model_features"]
        self.categorical_features = dict_saved["categorical_features"]

    #     self._log.info("TRAIN full model")
    #     model = self.fit(train_data=data, 
    #                      init_score=init_score)
