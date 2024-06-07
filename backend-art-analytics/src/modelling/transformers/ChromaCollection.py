from typing import List, Dict
import chromadb
import pandas as pd 
import numpy as np
from src.context import Context
from src.utils.timing import timing

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
                 data_name : str = "text",
                 n_top_results: int = 25):

        super().__init__(context=context, config=config)

        # embedding db 
        chroma_db = chromadb.HttpClient(host='localhost', port=8000)

        self.n_top_results = n_top_results
        self.step_size = 41000 # max batch size collection step size
        self.collection = chroma_db.get_or_create_collection(
                                                    name = data_name,
                                                    metadata={"hnsw:space": "cosine"})

    @timing
    def save_collection(self, df_desc : pd.DataFrame, 
                        embeddings : np.array) -> None:
        
        nbr_steps = df_desc.shape[0] //self.step_size + 1

        for i in range(nbr_steps):
            self._log.info(f"[DB EMBEDDING] : adding batch {i+1} / {nbr_steps} to chromadb")
            sub_df = df_desc.iloc[i*self.step_size:(i+1)*self.step_size]

            self.collection.add(
                embeddings=embeddings[i*self.step_size:(i+1)*self.step_size],
                documents=sub_df[self.name.total_description].tolist(),
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