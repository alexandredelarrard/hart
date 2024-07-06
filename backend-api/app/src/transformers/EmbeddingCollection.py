from typing import List, Dict
import pandas as pd 
import numpy as np
import langid
from src.context import Context
from src.utils.timing import timing
from src.constants.variables import (TEXT_DB_EN,
                                     TEXT_DB_FR,
                                     PICTURE_DB)

from src.utils.step import Step
from omegaconf import DictConfig


class EmbeddingCollection(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)

        self.n_top_results = self._config.embedding.n_top_neighbors

    def detect_language(self, text):
        langue, _ = langid.classify(text)
        if langue == "en":
            return TEXT_DB_EN
        elif langue == "fr":
            return TEXT_DB_FR
        else: 
            self._log.warning(f"Text is not in EN or FR {langue}, will take EN default")
            return TEXT_DB_EN
        
    def get_db_pict_name(self):
        return PICTURE_DB
    
    @timing
    def get_query(self, db_name):
        if db_name == PICTURE_DB:
            return """
                    BEGIN;
                    SET LOCAL hnsw.ef_search = 100;
                    SELECT "id_unique" AS ids, ("embedding" <=> %s::vector) AS distances 
                    FROM {table}
                    ORDER BY distances 
                    LIMIT 100
                    """
        else:
            return """
                    BEGIN;
                    SET LOCAL hnsw.ef_search = 100;
                    SELECT "id_item" AS ids, ("embedding" <=> %s::vector) AS distances 
                    FROM {table}
                    ORDER BY distances 
                    LIMIT 100
                    """
        
    @timing
    def query_collection_postgres(self, query: str, query_embedded: np.array, table: str) -> Dict:

        query = query.format(table=table)
       
        df = pd.read_sql(query, 
                         con=self._context.db_con, 
                         params=(query_embedded.tolist()[0], ))
        
        return {"ids": df["ids"].tolist(), "distances": df["distances"].tolist()}
    
    @timing
    def get_id_item_from_pict(self, liste_ids_pict):
        df_ids= pd.read_sql(f"SELECT \"ID_ITEM\", \"ID_UNIQUE\" FROM \"ALL_ITEMS\" WHERE \"ID_UNIQUE\" IN {tuple(liste_ids_pict)}", 
                         con=self._context.db_con)
        return df_ids["ID_ITEM"].tolist()
    
    @timing
    def multi_embedding_strat(self, result_picture, result_text):

        df_pict = pd.DataFrame().from_dict(result_picture)
        df_text = pd.DataFrame().from_dict(result_text)

        self._log.info(df_pict.shape, df_text.shape)
        df = df_pict.merge(df_text, on="ids", suffixes=("_PICT", "_TXT"), how="outer")
        
        for col in ["distances_PICT", "distances_TXT"]:
            max_dist = df[col].max()
            df[col] = df[col].fillna(max_dist)

        df["distances"] = df[["distances_PICT", "distances_TXT"]].mean(axis=1)
        df = df.sort_values("distances")
        self._log.info(df.shape)

        return {"ids": df["ids"].tolist(), "distances": df["distances"].tolist()}
