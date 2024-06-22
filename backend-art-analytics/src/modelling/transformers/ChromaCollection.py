from typing import List, Dict
from chromadb import Settings, HttpClient
import pandas as pd 
import numpy as np
from src.context import Context
from src.utils.timing import timing

from src.utils.step import Step
from omegaconf import DictConfig
from src.constants.variables import (CHROMA_PICTURE_DB_NAME,
                                     CHROMA_TEXT_DB_NAME)

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
                 type : str = "picture",
                 n_top_results: int = 25):

        super().__init__(context=context, config=config)

        # embedding db 
        chroma_db = HttpClient(host='localhost', 
                                port=8000,
                                settings=Settings(
                                    allow_reset=True,
                                    anonymized_telemetry=False,
                                ))

        self.n_top_results = n_top_results
        self.step_size = 41000 # max batch size collection step size

        if type == "picture":
            self.collection = chroma_db.get_or_create_collection(
                                                        name = CHROMA_TEXT_DB_NAME,
                                                        metadata={"hnsw:space": "cosine"})
        elif type == "text":
            self.collection = chroma_db.get_or_create_collection(
                                                        name = CHROMA_PICTURE_DB_NAME,
                                                        metadata={"hnsw:space": "cosine"})
        else:
            raise Exception("Only text of picture collections handled so far")
        
    @timing
    def save_collection(self, 
                        df_desc : pd.DataFrame, 
                        embeddings : np.array, 
                        is_document : bool = True) -> None:
        
        nbr_steps = df_desc.shape[0] //self.step_size + 1

        for i in range(nbr_steps):
            self._log.info(f"[DB EMBEDDING] : adding batch {i+1} / {nbr_steps} to chromadb")
            sub_df = df_desc.iloc[i*self.step_size:(i+1)*self.step_size]

            if not is_document:
                documents = [None]*sub_df.shape[0]
            else:
                documents = sub_df[self.name.total_description].tolist()

            self.collection.add(
                embeddings=embeddings[i*self.step_size:(i+1)*self.step_size],
                documents=documents,
                metadatas=recreate_dict(sub_df),
                ids=sub_df[self.name.id_unique].tolist()
            )
    
    @timing
    def query_collection(self, query_embedded : np.array) -> Dict:
        return self.collection.query(query_embeddings=query_embedded,
                                     n_results=self.n_top_results)

    @timing
    def delete_collection(self, list_ids):

        nbr_steps = len(list_ids) //self.step_size + 1
        for i in range(nbr_steps):
            self._log.info(f"[DB EMBEDDING] : Deleting batch {i+1} / {nbr_steps} to chromadb")
            sub_df = list_ids[i*self.step_size:(i+1)*self.step_size]
            self.collection.delete(ids=sub_df)