import numpy as np
import swifter
from pathlib import Path
from typing import List, Dict
import pandas as pd

pd.options.mode.copy_on_write = True

from src.context import Context
from src.utils.timing import timing

from omegaconf import DictConfig
from src.utils.utils_crawler import read_crawled_pickles, read_json
from src.utils.utils_extraction_gpt import handle_answer, homogenize_keys_name
from src.dataclean.transformers.GptCleaner import GPTCleaner


class StepCategoryGptInference(GPTCleaner):

    def __init__(self, context: Context, config: DictConfig):

        super().__init__(context=context, config=config)

        self.category = "reformulate"
        self.sql_table_name = self._config.table_names.gpt_translate_categorize
        self.clean_info_with_mapping = self._config.evaluator.info_to_mapping
        self.mappings = self._config.evaluator.cleaning_mapping

        self.save_queue_path = self._context.paths["LLM_EXTRACTED"] / Path(
            self.category
        )
        self.category_mapping_path = self._context.paths["LLM_TO_EXTRACT"] / Path(
            self._config.evaluator.category_mapping_path
        )
        self._mapping_path = self._context.paths["LLM_TO_EXTRACT"] / Path(
            self._config.evaluator.mappings_path[self.category.lower()]
        )

    @timing
    def run(self):

        # get col_mapping:
        self.col_mapping = read_json(self._mapping_path)
        self.cat_map = read_json(self.category_mapping_path)

        df_done = read_crawled_pickles(path=self.save_queue_path)

        # extract json from gpt answer
        df_done = self.eval_json(df_done)

        # get all features in the json
        df_done = self.extract_features(df_done)

        # keep the latest id_item
        df_done = self.deduplicate(df_done)

        # remove any missing output queried in the gpt category extract
        df_done = self.remove_missing(df_done)

        # map all categories to the listed item
        df_done = self.clean_category(df_done)

        # keep relevant columns
        del df_done["ANSWER"]

        self.save_infos_to_tables(df_done)

    @timing
    def eval_json(self, df_done):

        # evaluate string to Dict or List
        df_done["ANSWER"] = df_done[[self.name.id_item, "ANSWER"]].apply(
            lambda x: handle_answer(x), axis=1
        )
        df_done = df_done.loc[
            (df_done["ANSWER"] != "{}") & (df_done["ANSWER"].notnull())
        ]

        # remove lots of too many different objects
        nbr_objects = df_done["ANSWER"].apply(
            lambda x: len(x) if isinstance(x, List) else 1
        )
        self._log.info(nbr_objects.value_counts())
        df_done = df_done.loc[3 >= nbr_objects]

        # align multi objects with simple objects by exploding desc and keep thos existing
        df_done["ANSWER"] = df_done["ANSWER"].apply(
            lambda x: [x] if isinstance(x, Dict) else x
        )
        df_done = df_done.explode("ANSWER")

        # remove non dict answers since we asked for a JSON format
        is_dict = df_done["ANSWER"].apply(lambda x: isinstance(x, Dict))
        df_done = df_done.loc[is_dict]

        return df_done

    @timing
    def extract_features(self, df_done):

        # handle features element
        df_done = df_done.loc[df_done["ANSWER"].notnull()]

        # clean dict
        df_done["ANSWER"] = df_done["ANSWER"].swifter.apply(
            lambda x: homogenize_keys_name(x, self.col_mapping, smooth_text=False)
        )

        for col in self.col_mapping.keys():
            df_done[col.upper()] = df_done["ANSWER"].str.get(col)
            df_done[col.upper()] = df_done[col.upper()].apply(
                lambda x: ", ".join(x) if isinstance(x, List) else x
            )
            df_done[col.upper()] = np.where(
                df_done[col.upper()].isin(
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
                        "Null",
                        " ",
                        "non specified",
                        "not applicable",
                        "non specificato",
                    ]
                ),
                np.nan,
                df_done[col.upper()],
            )
        return df_done

    @timing
    def remove_missing(self, df_done):

        shape_0 = df_done.shape[0]

        df_done["FRENCH_TITLE"] = df_done["FRENCH_TITLE"].apply(
            lambda x: str(x).replace("Description de l'art:", "")
        )
        df_done["ENGLISH_TITLE"] = df_done["ENGLISH_TITLE"].apply(
            lambda x: str(x).replace("Art Description:", "")
        )

        df_done["FRENCH_TITLE"] = np.where(
            df_done["FRENCH_TITLE"].isin(
                [
                    "Sans titre",
                    "Description de l'art",
                    "Sans Titre",
                    "Description de l'art:",
                ]
            ),
            np.nan,
            df_done["FRENCH_TITLE"],
        )
        df_done["ENGLISH_TITLE"] = np.where(
            df_done["ENGLISH_TITLE"].isin(
                ["Untitled", "Art Description", "Art Description:"]
            ),
            np.nan,
            df_done["ENGLISH_TITLE"],
        )

        # remove all mvs in any column
        for col in df_done.columns:
            df_done = df_done.loc[df_done[col].notnull()]

        self._log.info(
            f"Removing {shape_0 - df_done.shape[0]}/{shape_0} observations due to missing info"
        )
        return df_done.reset_index(drop=True)

    def apply_mapping_func(self, vector, mapping_dict):
        return vector.swifter.apply(
            lambda x: self.exact_map_value_to_key(
                str(x).replace('"-"', '" "').replace('","', '""'), mapping_dict
            )
        )

    @timing
    def clean_category(self, df_done):

        # clean text in each category
        truncated_cat = df_done["OBJECT_CATEGORY"].apply(
            lambda x: self.pseudo_clean_category(x)
        )
        df_done["CLEAN_OBJECT_CATEGORY"] = self.apply_mapping_func(
            truncated_cat, self.cat_map
        )
        self._log.info(
            (
                f"Remaining missing mapping proportion \
                       {df_done['CLEAN_OBJECT_CATEGORY'].isnull().sum()*100/df_done.shape[0]:.2f}% \
                       ({df_done['CLEAN_OBJECT_CATEGORY'].isnull().sum()}/{df_done.shape[0]})"
            )
        )

        return df_done

    @timing
    def deduplicate(self, df_done):
        df_done = df_done.sort_values("FILE_CREATION_DATE", ascending=0)
        df_done = df_done.drop_duplicates(self.name.id_item)
        return df_done.reset_index(drop=True)

    @timing
    def save_infos_to_tables(self, df_done):

        # save a table mapping desc to specific category
        df_done["STATUS"] = np.where(
            df_done["CLEAN_OBJECT_CATEGORY"].isnull(), "KO", "OK"
        )
        self.remove_rows_sql_data(
            values=df_done[self.name.id_item].tolist(),
            column=self.name.id_item,
            table_name=self.sql_table_name,
        )
        self.write_sql_data(
            dataframe=df_done, table_name=self.sql_table_name, if_exists="append"
        )
