import numpy as np
import swifter
from typing import List
import pandas as pd
from pathlib import Path

pd.options.mode.copy_on_write = True

from omegaconf import DictConfig
from src.utils.utils_crawler import read_json
from src.dataclean.transformers.GptCleaner import GPTCleaner
from src.schemas.gpt_schemas import LlmExtraction, ColName
from src.schemas.gpt_cleaning import GptTranslateCategorize

from src.context import Context
from src.utils.timing import timing


class StepCleanGptInference(GPTCleaner):

    def __init__(self, context: Context, config: DictConfig, object: str = "painting"):

        super().__init__(context=context, config=config)

        self.object = object

        self.category_mapping_path = self._context.paths["LLM_TO_EXTRACT"] / Path(
            self._config.evaluator.category_mapping_path
        )

        self.sql_input_table = LlmExtraction.__tablename__

        if self.object == "reformulate":
            self.sql_output_table_name = GptTranslateCategorize.__tablename__
        else:
            self.sql_output_table_name = "_".join(
                [self._config.table_names.gpt_features_root, {self.object}]
            )

        self.clean_info_with_mapping = self._config.evaluator.info_to_mapping
        self.mappings = self._config.evaluator.cleaning_mapping
        self.cols_to_cm = self._config.evaluator.handle_cm
        self.cols_to_date = self._config.evaluator.handle_dates
        self.cols_to_float = self._config.evaluator.cols_to_float
        self.binary_cols = self._config.evaluator.binary_cols

        # category mapping
        self.mappings["object_category_mapping"] = read_json(self.category_mapping_path)

    @timing
    def run(self):

        query_string = self.get_query_string()
        df_done = self.read_sql_data(query_string)

        # extract json and features
        df_done = self.extract_features(df_done)
        df_done = self.deduplicate(df_done)

        # clean column values
        df_done = self.clean_dimensions(df_done)
        df_done = self.clean_dates(df_done)
        df_done = self.clean_text(df_done)
        df_done = self.clean_binary(df_done)
        df_done = self.clean_values(df_done)

        # save to sql table
        self.save_infos_to_tables(df_done)

    @timing
    def get_query_string(self):
        query = f"""SELECT {self.name.low_id_item}, {self.name.input}, {self.name.gpt_answer}, {self.name.date_run}
            FROM {self.sql_input_table}
            WHERE {self.name.prompt_schema}='{self.object}' """

        if self.object == "reformulate":
            query += f" OR {self.name.prompt_schema} IS NULL"

        return query

    @timing
    def extract_features(self, df_done):

        # handle features element
        df_done = df_done.loc[df_done[self.name.gpt_answer].notnull()]

        # from series of dict to dataframe
        df_answer = pd.json_normalize(df_done[self.name.gpt_answer])

        # Step 2: Concatenate the new DataFrame with the existing DataFrame
        df_done = pd.concat([df_done, df_answer], axis=1)

        # Step 3: Drop the original 'answer' column if needed
        df_done.drop(columns=[self.name.gpt_answer], inplace=True)

        # Step 4: clean values out of column generic way
        for col in df_done.columns:
            df_done[col] = np.where(
                df_done[col]
                .str.lower()
                .isin(
                    [
                        "n/a",
                        "unspecified",
                        "",
                        "unknown",
                        "none",
                        "not specified",
                        "'n/a'",
                        "null",
                        "not found",
                        "na",
                        "nan",
                        "undefined",
                        "null",
                        " ",
                        "non specified",
                        "not applicable",
                        "non specificato",
                        "sans titre",
                        "description de l'art",
                        "description de l'art:",
                        "untitled",
                        "art description",
                        "art description:",
                    ]
                ),
                np.nan,
                df_done[col],
            )

        return df_done

    @timing
    def clean_dimensions(self, df_done):
        df_columns = df_done.columns
        for column in self.cols_to_cm:
            column = self.col_names_with_category(column)
            if column in df_columns:
                df_done[column] = df_done[column].apply(
                    lambda x: self.handle_cm(str(x))
                )
        return df_done

    @timing
    def clean_dates(self, df_done):
        df_columns = df_done.columns
        for column in self.cols_to_date:
            column = self.col_names_with_category(column)
            if column in df_columns:
                df_done[column] = df_done[column].apply(
                    lambda x: self.clean_periode(str(x))
                )
        return df_done

    @timing
    def clean_text(self, df_done):
        df_columns = df_done.columns
        for function_mapping, column_to_clean in self.clean_info_with_mapping.items():
            for target_column, columns_name in column_to_clean.items():
                if len(columns_name) == 1:
                    col_name = self.col_names_with_category(target_column)

                    if col_name in df_columns:
                        self._log.info(f"CLEANING {col_name}")

                        mapping_dict = self.invert_mapping_dict(
                            self.mappings[function_mapping]
                        )

                        if function_mapping == "object_category_mapping":
                            truncate = df_done[col_name].swifter.apply(
                                lambda x: self.pseudo_clean_category(x)
                            )
                        else:
                            truncate = df_done[col_name]

                        df_done["clean_" + col_name] = truncate.map(mapping_dict)

                else:
                    col_name = self.col_names_with_category(target_column)

                    if col_name in df_columns:
                        self._log.info(f"CLEANING {target_column}")

                        mapping_dict = self.invert_mapping_dict(
                            self.mappings[function_mapping]
                        )
                        df_done["clean_" + col_name] = df_done[col_name].map(
                            mapping_dict
                        )

                        for other_col_name in columns_name[1:]:
                            other_col_name = self.col_names_with_category(
                                other_col_name
                            )
                            df_done["clean_" + col_name] = np.where(
                                df_done["clean_" + col_name].isnull(),
                                df_done[other_col_name].map(mapping_dict),
                                df_done["clean_" + col_name],
                            )
        return df_done

    @timing
    def clean_binary(self, df_done):
        df_columns = df_done.columns
        for column in self.binary_cols:
            column = self.col_names_with_category(column)
            if column in df_columns:
                df_done[column] = np.where(
                    df_done[column].isin(
                        [
                            "not marked",
                            "non signe",
                            "non signee",
                            "not signed",
                            "no",
                            "false",
                            "not dated",
                            "not",
                            "non",
                            "faux",
                            "unmarked",
                        ]
                    ),
                    False,
                    np.where(
                        df_done[column].isnull()
                        | df_done[column].isin(["none", "null", "nan"]),
                        np.nan,
                        True,
                    ),
                )
        return df_done

    @timing
    def clean_values(self, df_done):

        for col in self.cols_to_float:
            if col in df_done.columns:
                df_done[col] = df_done[col].apply(lambda x: self.eval_number(str(x)))

        # relation d'ordre sur la condition de l'objet
        if f"{self.object}_condition" in df_done.columns:
            df_done[f"{self.object}_condition"] = df_done[
                f"{self.object}_condition"
            ].map({"very good": 4, "good_": 3, "okay_": 2, "poor": 1})

        return df_done

    @timing
    def deduplicate(self, df_done):
        df_done = df_done.sort_values(self.name.date_run, ascending=0)
        df_done = df_done.drop_duplicates(self.name.low_id_item)
        return df_done.reset_index(drop=True)

    @timing
    def save_infos_to_tables(self, df_done):

        self.remove_rows_sql_data(
            values=df_done[self.name.low_id_item].tolist(),
            column=self.name.low_id_item,
            table_name=self.sql_output_table_name,
        )
        self.write_sql_data(
            dataframe=df_done, table_name=self.sql_output_table_name, if_exists="append"
        )

    ## frequent calls ##
    def col_names_with_category(self, col_name):
        if col_name[0] == "_":
            return self.object + col_name
        return col_name

    def apply_mapping_func(self, vector, mapping_dict):
        return vector.swifter.apply(
            lambda x: self.exact_map_value_to_key(str(x), mapping_dict)
        )
