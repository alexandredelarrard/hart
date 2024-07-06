import pandas as pd
import numpy as np
from tqdm import tqdm

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.Embedding import StepEmbedding
from src.modelling.transformers.ModelEvaluator import ModelEvaluator
from omegaconf import DictConfig


class StepKNNPriceEvaluator(Step):

    def __init__(self, context: Context, config: DictConfig, category: str = "vase"):

        super().__init__(context=context, config=config)

        self.category = category
        self.prompt_name = self._config.embedding.prompt_name
        self.n_top_results = 20

        self.step_embedding = StepEmbedding(context=context, config=config, type="text")
        self.evaluator = ModelEvaluator()

    def predict(self):

        df = self.read_sql_data(self._config.cleaning.full_data_auction_houses)
        sub_df = df.loc[
            df[self.name.total_description].apply(
                lambda x: " vase " in " " + str(x).lower() + " "
            )
        ].sample(frac=0.25)
        liste_text = (
            sub_df[self.name.total_description].apply(lambda x: x.lower()).tolist()
        )
        liste_ids_tested = sub_df[self.name.id_item].tolist()

        embeddings = self.step_embedding.get_text_embeddings(
            liste_text, prompt_name=self.prompt_name
        )

        # reshape results
        # text_results = self.collection.query_collection(embeddings)
        # TODO replace with postgres query
        df_results = self.clean_text_results(liste_ids_tested, text_results)

        df_estimate = (
            df_results[
                [
                    "ID_ITEM_ORIGIN",
                    self.name.eur_min_estimate,
                    self.name.eur_max_estimate,
                    self.name.eur_item_result,
                    "DISTANCE",
                ]
            ]
            .groupby("ID_ITEM_ORIGIN")
            .aggregate(
                {
                    self.name.eur_min_estimate: np.median,
                    self.name.eur_max_estimate: np.median,
                    self.name.eur_item_result: np.median,
                    "DISTANCE": np.median,
                }
            )
        )

        df_estimate = df_estimate.merge(
            sub_df[
                [
                    self.name.id_item,
                    self.name.eur_min_estimate,
                    self.name.eur_max_estimate,
                    self.name.eur_item_result,
                ]
            ],
            left_on="ID_ITEM_ORIGIN",
            right_on=self.name.id_item,
            how="left",
            validate="m:1",
            suffixes=("KNN_", ""),
        )
        df_estimate[self.name.auctionner_estimate] = df_estimate[
            [self.name.eur_max_estimate, self.name.eur_min_estimate]
        ].mean(axis=1)
        df_estimate = df_estimate.loc[df_estimate[self.name.eur_item_result] >= 10]

        df_estimate["TEST"] = df_estimate[
            [self.name.eur_min_estimate + "KNN_", self.name.eur_max_estimate + "KNN_"]
        ].mean(axis=1)

        # analyse results
        result_bias = self.evaluator.get_mean_bias(
            y_prediction=df_estimate[self.name.eur_item_result + "KNN_"],
            y_true=df_estimate[self.name.eur_item_result],
        )

        result_mape = self.evaluator.evaluation_mape_mean(
            y_prediction=df_estimate[self.name.eur_item_result + "KNN_"],
            y_true=df_estimate[self.name.eur_item_result],
        )
        test_mape = self.evaluator.evaluation_mape_mean(
            y_prediction=df_estimate["TEST"],
            y_true=df_estimate[self.name.eur_item_result],
        )
        min_mape = self.evaluator.evaluation_mape_mean(
            y_prediction=df_estimate[self.name.eur_min_estimate + "KNN_"] + 1,
            y_true=df_estimate[self.name.eur_min_estimate] + 1,
        )
        max_mape = self.evaluator.evaluation_mape_mean(
            y_prediction=df_estimate[self.name.eur_max_estimate + "KNN_"] + 1,
            y_true=df_estimate[self.name.eur_max_estimate] + 1,
        )

        result_std = self.evaluator.evaluation_mape_std(
            y_prediction=df_estimate[self.name.eur_item_result + "KNN_"],
            y_true=df_estimate[self.name.eur_item_result] + 1,
        )

        auctionner_mape = self.evaluator.evaluation_mape_mean(
            y_prediction=df_estimate[self.name.auctionner_estimate],
            y_true=df_estimate[self.name.eur_item_result],
        )

        print = f"\n OOS {embeddings.shape[0]}: "
        print += f" RESULT BASELINE MAPE = {auctionner_mape:.1f}\n"
        print += f" TEST KNN MAPE = {test_mape:.1f}\n"
        print += f" RESULT KNN MAPE = {result_mape:.1f} +/- {result_std:.1f}\n"
        print += f" MIN KNN MAPE = {min_mape:.1f}\n"
        print += f" MAX KNN MAPE = {max_mape:.1f}\n"
        print += f" KNN BIAS = {result_bias:.1f}\n"
        print += f" KNN DISTANCE Median = {df_estimate['DISTANCE'].median():.2f}\n"

        self._log.info(print)

    def clean_text_results(self, liste_ids_tested, text_results):

        liste_dfs = []
        for i in tqdm(range(len(text_results["distances"]))):
            df_new_result = pd.DataFrame(text_results["metadatas"][i])
            df_new_result["DISTANCE"] = text_results["distances"][i]
            df_new_result["ID_ITEM_ORIGIN"] = liste_ids_tested[i]
            liste_dfs.append(df_new_result)

        df_results = pd.concat(liste_dfs, axis=0, ignore_index=True)

        # exclude elements tested in the answer
        df_results = df_results.loc[
            df_results[self.name.id_item] != df_results["ID_ITEM_ORIGIN"]
        ]

        for col in [
            self.name.eur_min_estimate,
            self.name.eur_max_estimate,
            self.name.eur_item_result,
        ]:
            df_results[col] = (
                df_results[col].replace("", 0).astype(float).replace(0, np.nan)
            )

        return df_results
