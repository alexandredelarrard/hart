import os 

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

        self.vector = "PICTURES"
        self.step_embedding = StepEmbedding(context=context, config=config, 
                                            type="picture")
        self.data_retreiver = DatasetRetreiver(context=context, config=config)
        self.chroma_collection = ChromaCollection(context=self._context,
                                                 data_name=CHROMA_PICTURE_DB_NAME, 
                                                 config=self._config)
        
    @timing
    def run(self):

        # exrtract data from dbeaver, ensure not done and sample to test
        df_desc = self.data_retreiver.get_all_pictures(data_name=self.full_data)
        df_desc = df_desc.sample(frac=0.5)
        df_desc = self.filter_out_embeddings_done(df_desc)
        df_desc = self.check_is_file(df_desc)

        # create text embedding
        self.embeddings = self.step_embedding.get_picture_embedding(df_desc[self.vector].tolist())

        #save to chroma db
        # Unique ID is the ID picture 
        self.chroma_collection.save_collection(df_desc.fillna(""), self.embeddings)

        return df_desc 
    
    def read_data_trained(self):
        df_desc = self.data_retreiver.get_text_to_cluster(data_name= "PICTURES_CATEGORY_20_04_2024")
        return df_desc

        
    def filter_out_embeddings_done(self, df_desc):
        collection_infos = self.chroma_collection.collection.get()
        done_ids = collection_infos["ids"].apply(lambda x: x.split("_")[0])
        df_desc = df_desc.loc[~df_desc[self.name.id_picture].isin(done_ids)]
        return df_desc

    @timing
    def check_is_file(self, df_desc):
        if self.vector not in df_desc.columns:
            df_desc[self.vector] = df_desc[["SELLER", "ID_PICTURE"]].apply(lambda x : f"D:/data/{x['SELLER']}/pictures/{x['ID_PICTURE']}.jpg", axis=1)
        
        exists_pict = df_desc[self.vector].swifter.apply(lambda x : os.path.isfile(x))
        df_desc = df_desc[exists_pict].reset_index(drop=True)
        return df_desc
    