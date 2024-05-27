from tqdm import tqdm

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.Embedding import StepEmbedding
from src.utils.utils_crawler import move_picture
from src.utils.dataset_retreival import DatasetRetreiver
from src.modelling.transformers.ChromaCollection import ChromaCollection

from src.constants.variables import (CHROMA_PICTURE_DB_NAME)

from omegaconf import DictConfig

class StepFillChromaPictures(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)
        self.full_data = self._config.cleaning.full_data_auction_houses

        self.root = self._config.crawling.root_path
        self.vector = "pict_path"
        self.step_embedding = StepEmbedding(context=context, config=config, 
                                            type="picture")
        self.data_retreiver = DatasetRetreiver(context=context, config=config)
        self.chroma_collection = ChromaCollection(context=self._context,
                                                 data_name=CHROMA_PICTURE_DB_NAME, 
                                                 config=self._config)
        
    @timing
    def run(self):

        # exrtract data from dbeaver, ensure not done and sample to test # 11+ M picts
        df_desc = self.data_retreiver.get_all_pictures(data_name=self.full_data, vector=self.vector, limit=3000000)
        df_desc = df_desc.drop_duplicates(self.name.id_unique)
        df_desc = self.filter_out_embeddings_done(df_desc)

        # create text embedding
        self.embeddings = self.step_embedding.get_picture_embedding(df_desc[self.vector].tolist())

        #save to chroma db
        self.chroma_collection.save_collection(df_desc.fillna(""), self.embeddings)

    def read_data_trained(self):
        df_desc = self.data_retreiver.get_text_to_cluster(data_name= "PICTURES_CATEGORY_20_04_2024")
        return df_desc
        
    def filter_out_embeddings_done(self, df_desc):
        collection_infos = self.chroma_collection.collection.get()
        done_ids = collection_infos["ids"]
        df_desc = df_desc.loc[~df_desc[self.name.id_picture].isin(done_ids)]
        self._log.info(f"DONE IDS in CHROMA DB = {len(done_ids)}")
        return df_desc
