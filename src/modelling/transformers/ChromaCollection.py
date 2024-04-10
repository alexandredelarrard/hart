from typing import List
from src.context import Context
from src.utils.timing import timing

from src.utils.step import Step
from omegaconf import DictConfig


class ChromaCollection(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 data_name : str = "drouot"):

        super().__init__(context=context, config=config)

        self.n_top_results = 20
        self.step_size = 41000 # max batch size collection step size
        self.collection = self._context.chroma_db.get_or_create_collection(
                                                    name = data_name,
                                                    metadata={"hnsw:space": "cosine"})

    @timing
    def save_collection(self, df_desc, embeddings):
        
        nbr_steps = df_desc.shape[0] //self.step_size + 1

        for i in range(nbr_steps):

            self._log.info(f"[DB EMBEDDING] : adding batch {i} / {nbr_steps} to chromadb")
            sub_df = df_desc.iloc[i*self.step_size:(i+1)*self.step_size]

            self.collection.add(
                embeddings=embeddings[i*self.step_size:(i+1)*self.step_size],
                documents=sub_df[self.name.total_description].tolist(),
                metadatas=sub_df.to_dict(orient="records"),
                ids=sub_df[self.name.id_item].tolist()
            )
    
    @timing
    def query_collection(self, query_embedded):
        return self.collection.query(query_embeddings=query_embedded,
                                     n_results=self.n_top_results)
