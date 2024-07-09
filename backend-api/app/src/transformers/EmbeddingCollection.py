import langid
import pandas as pd
import math
from typing import Dict, Any
import numpy as np
from src.context import Context
from src.utils.timing import timing
from src.constants.variables import TEXT_DB_EN, TEXT_DB_FR, PICTURE_DB
from src.constants.models import EmbeddingsResults, BaseResult

from src.utils.step import Step
from omegaconf import DictConfig


class EmbeddingCollection(Step):

    def __init__(self, context: Context, config: DictConfig):

        super().__init__(context=context, config=config)

        self.n_top_results = self._config.embedding.n_top_neighbors
        self.full_data = self._config.cleaning.full_data_auction_houses
        self.table_id = {
            PICTURE_DB: self._config.cleaning.full_data_auction_houses,
            TEXT_DB_FR: self._config.cleaning.full_data_per_item,
            TEXT_DB_EN: self._config.cleaning.full_data_per_item,
        }
        self.unique_id_type = {
            PICTURE_DB: self.name.id_unique,
            TEXT_DB_FR: self.name.id_item,
            TEXT_DB_EN: self.name.id_item,
        }

    def detect_language(self, text):
        langue, _ = langid.classify(text)
        if langue == "en":
            return TEXT_DB_EN
        elif langue == "fr":
            return TEXT_DB_FR
        else:
            self._log.warning(f"Text is not in EN or FR {langue}, will take EN default")
            return TEXT_DB_EN

    @timing
    def multi_embedding_strat(
        self, result_image: pd.DataFrame, result_text: pd.DataFrame
    ) -> pd.DataFrame:

        df = result_image.merge(
            result_text,
            on=self.name.id_item.lower(),
            suffixes=("_PICT", "_TXT"),
            how="outer",
        )

        for col in ["distance_PICT", "distance_TXT"]:
            max_dist = df[col].max()
            df[col] = df[col].fillna(max_dist)

        df["distance"] = df[["distance_PICT", "distance_TXT"]].mean(axis=1)
        df = df.sort_values("distance")

        return df[[self.name.id_item.lower(), self.name.id_picture.lower(), "distance"]]

    @timing
    def fill_EmbeddingsResults(self, liste_results):

        def filter_non_null_values(data: Dict[str, Any]) -> Dict[str, Any]:
            return {
                k: v
                for k, v in data.items()
                if v is not None and not (isinstance(v, float) and math.isnan(v))
            }

        return EmbeddingsResults(
            answer={
                k: BaseResult(**filter_non_null_values(v))
                for k, v in liste_results.items()
            }
        )
