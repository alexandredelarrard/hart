import pandas as pd

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.TrainerLightgbm import TrainLightgbmModel

from src.constants.variables import DATE_FORMAT
from omegaconf import DictConfig


class StepGBMPriceEvaluator(Step):

    def __init__(self, context: Context, config: DictConfig, category: str = "vase"):

        super().__init__(context=context, config=config)
        self.category = category

    def training(self, database_name="TEST_0.05_CLEAN_VASE"):

        df = self.read_sql_data(database_name)
        df_price = self.get_pricing_info()

        # merge dataframe together & ensure output is there
        df = self.shape_data(df, df_price)
        df = df.loc[df[self.name.eur_item_result].between(10, 200000)]
        df = df.loc[df[self.name.is_item_result] == 1]

        # Trainer
        self.trainer = TrainLightgbmModel(config=self._config, category=self.category)
        self.get_baseline(df)

        # 5 fold to get error rate
        results = self.trainer.modelling_cross_validation(data=df)
        results["PREDICTION"] = (results["PREDICTION"] / 10).round(0) * 10

        # predictions global error rate
        self.trainer.evaluate_model(
            self.trainer.model_parameters,
            results["PREDICTION"],
            results[self.trainer.target_name],
        )

        self.trainer.fit(df)
        self.trainer.get_model_shap(self.trainer.model, data=df)

        a = results[
            ["PREDICTION", self.trainer.target_name, self.name.auctionner_estimate]
        ]

        self.trainer.evaluation_mape_mean(a["EXPERT_ESTIMATION"], a["EUR_FINAL_RESULT"])

    def shape_data(self, df, df_price):
        df = df.merge(df_price, on=self.name.id_item, how="left", validate="1:1")
        df = df.loc[df["EUR_FINAL_RESULT"].notnull()]
        df[self.name.sold_year] = pd.to_datetime(
            df[self.name.date], format=DATE_FORMAT
        ).dt.year
        df[self.name.auctionner_estimate] = df[
            [self.name.eur_max_estimate, self.name.eur_min_estimate]
        ].mean(axis=1)
        return df

    def get_baseline(self, df):

        df_real_result = df.loc[df[self.name.is_item_result] == 1]

        if df_real_result.shape[0] != 0:
            mape = self.trainer.evaluation_mape_mean(
                df_real_result[self.name.auctionner_estimate],
                df_real_result[self.trainer.target_name],
            )
            std = self.trainer.evaluation_mape_std(
                df_real_result[self.name.auctionner_estimate],
                df_real_result[self.trainer.target_name],
            )
            self._log.info(
                f"BASELINE ERROR = {mape:.2f} +/- {std:.2f} EUR ({df_real_result.shape[0]*100/df.shape[0]:.1f})"
            )

        else:
            self._log.warning(
                "No BASELINE can be calculated since all results are duduced from center of estimates "
            )

    def get_pricing_info(self):

        raw_query = str.lower(getattr(self.sql_queries.SQL, "get_all_for_pricing"))
        formatted_query = self.sql_queries.format_query(
            raw_query,
            {
                "id_item": self.name.id_item,
                "eur_min_estimate": self.name.eur_min_estimate,
                "eur_max_estimate": self.name.eur_max_estimate,
                "eur_item_result": self.name.eur_item_result,
                "is_item_result": self.name.is_item_result,
                "currency": self.name.currency,
                "auction_date": self.name.date,
                "localisation": self.name.localisation,
                "seller": self.name.seller,
                "table_name_full": self._config.cleaning.full_data_auction_houses,
            },
        )

        # 3. Fetch results
        self._log.info(formatted_query)
        return self.read_sql_data(formatted_query)
