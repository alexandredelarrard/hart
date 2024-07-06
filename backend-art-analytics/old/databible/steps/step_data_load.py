from typing import List, Dict
from omegaconf import DictConfig
import pandas as pd
import ast

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.utils.utils_dataframe import homogenize_columns, transform_types


class StepDataLoad(Step):

    def __init__(self, config: DictConfig, context: Context):

        super().__init__(context=context, config=config)

    @timing
    def run(self):

        # initialize the drivers
        data_dict = self.load_datas()

        return data_dict

    @timing
    def load_datas(self):

        cleaning_methods = [
            method for method in dir(StepDataLoad) if "cleaning" in method
        ]

        for granularity, data_name in self._config.flat_file.insee.items():

            for data_name, data_config in self._config.flat_file.insee[
                granularity
            ].items():
                dataframe = self.load_data(
                    data_config=data_config,
                    names=self._config.naming[granularity][data_name],
                    dtypes=self._config.dtypes[granularity][data_name],
                )

                if f"cleaning_{granularity}_{data_name}" in cleaning_methods:
                    self._log.info(f"cleaning during loading of table {data_name}")
                    dataframe = ast.literal_eval(
                        f"self.cleaning_{granularity}_{data_name}"
                    )(dataframe)

                if "table_name" not in data_config.keys():
                    data_config.table_name = "_".join(
                        [granularity.upper(), data_name.upper()]
                    )

                self.write_sql_data(
                    dataframe=dataframe, table_name=data_config.table_name
                )

    def load_data(self, data_config, names: List = None, dtypes: Dict = None):

        kwargs = {}
        if "na_values" in data_config.keys():
            kwargs["na_values"] = data_config.na_values

        if dtypes:
            kwargs["dtype"] = dict(dtypes)

        try:
            df = pd.read_csv(
                data_config.path,
                sep=data_config.sep,
                on_bad_lines="warn",
                header=0,
                **kwargs,
            )
            df.columns = homogenize_columns(list(names.values()))

        except Exception as e:
            raise Exception(f"Could not read data {data_config['table_name']}", e)

        self._log.info(f"Read csv file {data_config.table_name} done")

        return df

    @timing
    def cleaning_carreaux_200m_met(self, df):
        # split insee code to have carreaux per insee code
        df["LCOG_GEO"] = df["LCOG_GEO"].apply(
            lambda x: [str(x)[i : i + 5] for i in range(0, len(str(x)), 5)]
        )
        df = df.explode("LCOG_GEO")
        return df

    @timing
    def cleaning_carreaux_200m_reun(self, df):
        # split insee code to have carreaux per insee code
        df["LCOG_GEO"] = df["LCOG_GEO"].apply(
            lambda x: [str(x)[i : i + 5] for i in range(0, len(str(x)), 5)]
        )
        df = df.explode("LCOG_GEO")
        return df

    @timing
    def cleaning_carreaux_200m_mart(self, df):
        # split insee code to have carreaux per insee code
        df["LCOG_GEO"] = df["LCOG_GEO"].apply(
            lambda x: [str(x)[i : i + 5] for i in range(0, len(str(x)), 5)]
        )
        df = df.explode("LCOG_GEO")
        return df

    @timing
    def cleaning_carreaux_1km_met(self, df):
        # split insee code to have carreaux per insee code
        df["LCOG_GEO"] = df["LCOG_GEO"].apply(
            lambda x: [str(x)[i : i + 5] for i in range(0, len(str(x)), 5)]
        )
        df = df.explode("LCOG_GEO")
        return df

    @timing
    def cleaning_carreaux_1km_reun(self, df):
        # split insee code to have carreaux per insee code
        df["LCOG_GEO"] = df["LCOG_GEO"].apply(
            lambda x: [str(x)[i : i + 5] for i in range(0, len(str(x)), 5)]
        )
        df = df.explode("LCOG_GEO")
        return df

    @timing
    def cleaning_carreaux_1km_mart(self, df):
        # split insee code to have carreaux per insee code
        df["LCOG_GEO"] = df["LCOG_GEO"].apply(
            lambda x: [str(x)[i : i + 5] for i in range(0, len(str(x)), 5)]
        )
        df = df.explode("LCOG_GEO")
        return df
