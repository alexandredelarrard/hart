from typing import List, Dict
import pandas as pd 
import numpy as np
from src.context import Context
from src.utils.timing import timing
from src.utils.constants import (CHROMA_PICTURE_DB_NAME, 
                                 CHROMA_TEXT_DB_NAME)

from src.utils.step import Step
from omegaconf import DictConfig

# just needed to ensure all keys are string. Chroma bug
def recreate_dict(sub_df : pd.DataFrame) -> List:
    
    all_meta = []
    for element in sub_df.to_dict(orient="records"):
        redo_meta_data = {}
        for k, value in element.items():
            redo_meta_data[str(k)] = value
        all_meta.append(redo_meta_data)
    return all_meta

class ChromaCollection(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 n_top_results: int = 48):

        super().__init__(context=context, config=config)

        self.n_top_results = n_top_results
        self.step_size = 41000 # max batch size collection step size
        self.text_collection = context.chroma_client.get_or_create_collection(
                                                    name = CHROMA_TEXT_DB_NAME,
                                                    metadata={"hnsw:space": "cosine"})
        
        self.picture_collection = context.chroma_client.get_or_create_collection(
                                                    name = CHROMA_PICTURE_DB_NAME,
                                                    metadata={"hnsw:space": "cosine"})

    @timing
    def save_collection(self, df_desc : pd.DataFrame, 
                        embeddings : np.array) -> None:
        
        nbr_steps = df_desc.shape[0] //self.step_size + 1

        for i in range(nbr_steps):
            self._log.info(f"[DB EMBEDDING] : adding batch {i+1} / {nbr_steps} to chromadb")
            sub_df = df_desc.iloc[i*self.step_size:(i+1)*self.step_size]

            self.picture_collection.add(
                embeddings=embeddings[i*self.step_size:(i+1)*self.step_size],
                documents=sub_df[self.name.total_description].tolist(),
                metadatas=recreate_dict(sub_df),
                ids=sub_df[self.name.id_unique].tolist()
            )
    
    @timing
    def query_collection(self, query_embedded : np.array) -> Dict:
        return self.picture_collection.query(query_embeddings=query_embedded,
                                            n_results=self.n_top_results)
