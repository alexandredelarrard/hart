import pandas as pd
from sklearn import metrics
import matplotlib.pyplot as plt
import shap
import numpy as np
import logging


class ModelEvaluator(object):
    """
    Wrapper around LightGBM model responsible for
        * fitting the LightGBM model on in put data.
        * evaluating model performance on a tests dataset.
        * Training on the overall dataset if no test set is given

    Arguments:
        object {[type]} --
    """

    def get_model_shap(self, model, data):

        try:
            feature_names = model.booster_.feature_name()
        except Exception:
            feature_names = model.feature_name()

        valid_x = data[feature_names]
        shap_values = shap.TreeExplainer(model).shap_values(valid_x)
        shap.summary_plot(shap_values, valid_x)
        plt.show()
        return shap_values

    def get_output_distribution(self, y_prediction, y_true):

        # evaluate results with plot importance
        pd.Series(y_prediction).hist(alpha=0.7, bins=30)
        pd.Series(y_true).hist(alpha=0.7, bins=30)
        plt.show()

    def get_mean_absolute_bias(self, y_prediction, y_true):
        return np.mean(abs(y_true - y_prediction))

    def get_mean_bias(self, y_prediction, y_true):
        return np.mean(y_true - y_prediction)

    def evaluation_mape_mean(self, y_prediction, y_true):
        """
        We use absolute percentage error to evaluate model performance.
        """
        return np.mean(abs(y_true - y_prediction) * 100 / y_true)

    def evaluation_mape_std(self, y_prediction, y_true):
        """
        We use absolute percentage error to evaluate model performance.
        """
        return np.std(abs(y_true - y_prediction) * 100 / y_true)

    def evaluation_auc(self, y_prediction, y_true):
        """Calculate ROC AUC for binary target

        Args:
            true ([int]): [binary target to predict ]
            pred ([float]): [predicted probability of the model]

        Returns:
            [float]: [AUC]
        """
        fpr, tpr, thresholds = metrics.roc_curve(y_true, y_prediction, pos_label=1)
        auc = metrics.auc(fpr, tpr)
        return auc

    def evaluate_model(self, model_parameters, y_prediction, y_true):
        """
        Plot feature importances and log error metrics.
        """

        # evaluate results based on evaluation metrics
        if model_parameters["objective"] == "regression":

            logging.info("_" * 60)
            mean_absolute_bias = self.get_mean_absolute_bias(y_prediction, y_true)
            mean_bias = self.get_mean_bias(y_prediction, y_true)
            metrique = model_parameters["eval_metric"]

            if metrique == "mape":
                error = (
                    metrics.mean_absolute_percentage_error(y_true, y_prediction) * 100
                )
            elif metrique == "rmse":
                error = metrics.mean_squared_error(y_true, y_prediction) * 100
            elif metrique == "logrmse":
                error = metrics.root_mean_squared_log_error(y_true, y_prediction)
            else:
                self.log.warning(
                    "Please choose an evaluation in rmse, mape, logrmse. Will take mape by default"
                )
                error = metrics.mean_absolute_percentage_error(y_true, y_prediction)

            logging.info(
                f"EVALUATION : ERROR {metrique}= {error:.2f} | BIAS= {mean_bias:.2f} | ABS_BIAS= {mean_absolute_bias:.2f}"
            )
            logging.info("_" * 60)
        else:
            auc = self.evaluation_auc(y_prediction, y_true)
            logging.info("_" * 60)
            logging.info(f"AUC = {auc:.3f}")
            logging.info("_" * 60)
