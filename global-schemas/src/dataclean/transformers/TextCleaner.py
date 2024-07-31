from typing import List, Dict
import pandas as pd
import re
from datetime import datetime
import numpy as np
import swifter

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from src.constants.variables import currencies, LISTE_WORDS_REMOVE
from omegaconf import DictConfig

from src.utils.utils_dataframe import (
    clean_useless_text,
    remove_lot_number,
    remove_dates_in_parenthesis,
    clean_shorten_words,
    remove_spaces,
    remove_rdv,
    clean_quantity,
    clean_dimensions,
)


class TextCleaner(Step):

    def __init__(self, context: Context, config: DictConfig):

        super().__init__(context=context, config=config)
        self.year = datetime.today().year

    def get_list_element_from_text(self, variable, liste=currencies):
        return variable.apply(
            lambda x: (
                re.findall(liste, str(x))[0]
                if len(re.findall(liste, str(x))) > 0
                else np.nan
            )
        )

    def get_estimate(self, variable, min_max: str = "min"):

        def clean_thousands(x):
            return str(x).replace(" ", "").replace(",", "").replace("\u202f", "")

        if min_max.lower() == "min":
            return variable.apply(
                lambda x: (
                    re.findall("\\d+", clean_thousands(x))[0]
                    if len(re.findall("\\d+", clean_thousands(x))) > 0
                    else np.nan
                )
            )
        elif min_max.lower() == "max":
            return variable.apply(
                lambda x: (
                    re.findall("\\d+", clean_thousands(x))[1]
                    if len(re.findall("\\d+", clean_thousands(x))) > 1
                    else np.nan
                )
            )
        else:
            raise Exception("EITHER MIN OR MAX value for min_max")

    def get_splitted_infos(self, variable, index, sep="\n"):
        return pd.DataFrame(variable.fillna("").str.split(sep).tolist(), index=index)

    @timing
    def remove_missing_values(self, df, important_cols: List = []):

        if len(important_cols) == 0:
            important_cols = [self.name.url_full_detail, self.name.item_result]

        if self.check_cols_exists(important_cols, df.columns):
            shape_0 = df.shape[0]
            for i, col in enumerate(important_cols):
                if i == 0:
                    filter_missing = df[col].notnull()
                else:
                    filter_missing = (filter_missing) * (df[col].notnull())

            df = df.loc[filter_missing].reset_index(drop=True)
            shape_1 = df.shape[0]
            self._log.info(
                f"REMOVING {shape_0 - shape_1} \
                        ({(shape_0-shape_1)*100/shape_0:.2f}%) OBS due to lack of curcial infos"
            )
            return df
        else:
            missing_cols = set(important_cols) - set(df.columns)
            raise Exception(f"FOLLOWING COLUMN(S) IS MISSING {missing_cols}")

    @timing
    def clean_estimations(self, df: pd.DataFrame, liste_exceptions: List = []):

        important_cols = [
            self.name.item_result,
            self.name.min_estimate,
            self.name.max_estimate,
        ]

        if self.check_cols_exists(important_cols, df.columns):
            for col in important_cols:
                df[col] = np.where(
                    df[col]
                    .apply(lambda x: str(x).strip().lower())
                    .isin(liste_exceptions),
                    np.nan,
                    df[col],
                )
                df[col] = df[col].astype(float)
                df[col] = np.where(df[col] > 0, df[col], np.nan)

            df[self.name.is_item_result] = 1 * (df[self.name.item_result].notnull())
            df[self.name.item_result] = np.where(
                df[self.name.item_result].isnull(),
                df[[self.name.min_estimate, self.name.max_estimate]].mean(axis=1),
                df[self.name.item_result],
            )
            return df
        else:
            missing_cols = set(important_cols) - set(df.columns)
            raise Exception(f"FOLLOWING COLUMN(S) IS MISSING {missing_cols}")

    @timing
    def extract_currency(self, df):

        currency_col = (
            df[self.name.result]
            .str.replace("€", " EUR")
            .replace("$", " USD")
            .replace("£", " GBP")
        )
        df[self.name.currency] = self.get_list_element_from_text(currency_col)
        df = self.filter_wrong_currency(df)

        # redo with estimate col col
        currency_col = (
            df[self.name.estimate]
            .str.replace("€", " EUR")
            .replace("$", " USD")
            .replace("£", " GBP")
        )
        currency_estimate = self.get_list_element_from_text(currency_col)

        # concatenate results
        df[self.name.currency] = np.where(
            df[self.name.currency].isnull(),
            currency_estimate,
            df[self.name.currency],
        )
        df = self.filter_wrong_currency(df)

        return df

    def filter_wrong_currency(self, df):
        df[self.name.currency] = np.where(
            df[self.name.currency]
            .str.lower()
            .isin(
                [
                    "estimation : manquante",
                    "this lot has been withdrawn from auction",
                    "estimate on request",
                    "no result",
                    "no reserve",
                    "estimate upon request",
                    "estimate unknown",
                ]
            ),
            np.nan,
            df[self.name.currency],
        )
        return df

    @timing
    def clean_description(self, df):

        for col in [
            self.name.item_title,
            self.name.item_description,
            self.name.detailed_title,
            self.name.detailed_description,
        ]:
            if col in df.columns:
                df[col] = np.where(
                    df[col].str.lower().isin(LISTE_WORDS_REMOVE), np.nan, df[col]
                )
            else:
                self._log.debug(f"MISSING COL {col} in df for extract infos cleaning")

        return df

    def check_cols_exists(self, cols_a, cols_b):
        return len(set(cols_a).intersection(set(cols_b))) == len(cols_a)

    def renaming_dataframe(self, df, mapping_names):
        return df.rename(columns=mapping_names)

    @timing
    def remove_features(self, df, list_features):
        to_drop = set(list_features).intersection(df.columns)
        if len(to_drop) == len(list_features):
            df = df.drop(list_features, axis=1)
        else:
            missing = set(list_features) - set(to_drop)
            self._log.warning(f"CANNOT DROP {missing} : column MISSING")
            df = df.drop(list(to_drop), axis=1)
        return df

    @timing
    def extract_estimates(self, df):

        if self.name.estimate not in df.columns and self.name.result not in df.columns:
            raise Exception(
                f"Need to provide either {self.name.estimate} or {self.name.result} in the dataframe toe deduce price estimate"
            )

        if self.name.result not in df.columns:
            self._log.warning(
                f"{self.name.result} not in df columns, will take {self.name.estimate} as proxy for price estimate"
            )
            df[self.name.result] = df[self.name.estimate]

        df[self.name.item_result] = self.get_estimate(
            df[self.name.result], min_max="min"
        )

        if self.name.estimate not in df.columns:
            self._log.warning(
                f"{self.name.estimate} not in df columns, will take {self.name.result} as proxy for price estimate"
            )
            df[self.name.estimate] = df[self.name.result]

        df[self.name.min_estimate] = self.get_estimate(
            df[self.name.estimate], min_max="min"
        )
        df[self.name.max_estimate] = self.get_estimate(
            df[self.name.estimate], min_max="max"
        )
        df[self.name.max_estimate] = np.where(
            df[self.name.max_estimate].apply(lambda x: str(x).isdigit()),
            df[self.name.max_estimate],
            df[self.name.min_estimate],
        )
        return df

    @timing
    def homogenize_lot_number(self, df):
        df[self.name.lot] = df[self.name.lot].fillna(-1).astype(int)

        def reindex_lots(group):
            group = group.sort_values(by=self.name.lot).reset_index(drop=True)
            group["lot"] = range(1, len(group) + 1)
            return group

        df = df.sort_values([self.name.low_id_auction, self.name.lot]).reset_index(
            drop=True
        )
        df = df.groupby(self.name.low_id_auction, group_keys=False).apply(reindex_lots)

        df[self.name.lot] = np.where(df[self.name.lot] == -1, np.nan, df["lot"])
        del df["lot"]
        return df

    @timing
    def clean_text_description(self, df):

        # fill title with item title first then detailed title
        df[self.name.detailed_title] = np.where(
            df[self.name.item_title].isnull(),
            df[self.name.detailed_title],
            df[self.name.item_title],
        )

        # fill description with detailed desc then item desc
        df[self.name.total_description] = np.where(
            df[self.name.detailed_description].isnull(),
            df[self.name.item_description],
            df[self.name.detailed_description],
        )

        # clean both
        for col in [self.name.detailed_title, self.name.total_description]:
            df[col] = df[col].swifter.apply(lambda x: self.clean_row_description(x))
            df[col] = np.where(df[col].isin(["None", "", "nan"]), np.nan, df[col])
        return df

    def clean_row_description(self, x: str) -> str:

        x = clean_useless_text(x)
        x = remove_lot_number(x)
        x = remove_dates_in_parenthesis(x)
        x = clean_dimensions(x)
        x = clean_quantity(x)
        x = clean_shorten_words(x)
        x = remove_spaces(x)
        x = remove_rdv(x)

        return x

    # Function to try multiple date formats
    def try_multiple_formats(self, date_str, formats):
        for fmt in formats:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except ValueError as e:
                continue
        return None
