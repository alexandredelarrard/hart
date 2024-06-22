from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.Embedding import StepEmbedding
from src.utils.dataset_retreival import DatasetRetreiver
from src.modelling.transformers.ChromaCollection import ChromaCollection

from omegaconf import DictConfig

class StepFillChromaPictures(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 type : str = "picture", #picture or text
                 ):

        super().__init__(context=context, config=config)
        self.full_data = self._config.cleaning.full_data_auction_houses

        self.type = type
        self.root = self._config.crawling.root_path
        
        self.step_embedding = StepEmbedding(context=context, 
                                            config=config, 
                                            type=type)
        self.data_retreiver = DatasetRetreiver(context=context, config=config)
        self.chroma = ChromaCollection(context=self._context,
                                        config=self._config,
                                        type=type,
                                        n_top_results=25)
    
    @timing
    def run(self):

        # exrtract data from dbeaver, ensure not done and sample to test # 11+ M picts
        df_desc = self.get_data_for_chroma()
        df_desc = self.filter_out_embeddings_done(df_desc)

        # create text embedding
        self.embeddings = self.step_embedding.get_picture_embedding(df_desc[self.vector].tolist())

        #save to chroma db
        self.chroma.save_collection(df_desc.fillna(""), 
                                    self.embeddings, 
                                    is_document=False)

    def get_data_for_chroma(self):
        if self.type == "picture":
            self.vector = "pict_path"
            df_desc = self.data_retreiver.get_all_pictures(data_name=self.full_data, vector=self.vector, limit=4000000)
            return df_desc.drop_duplicates(self.name.id_unique)
        elif self.type=="text":
            self.vector=self.name.total_description
            df_desc = self.data_retreiver.get_all_text(data_name=self.full_data, vector=self.vector, limit=4000000)
            df_desc = df_desc.loc[df_desc[self.vector].str.length > 20]
            return df_desc.drop_duplicates(self.name.id_item)
        raise Exception("either text or picture for get data in chroma fill")

    def read_data_trained(self):
        df_desc = self.data_retreiver.get_text_to_cluster(data_name= "PICTURES_CATEGORY_20_04_2024")
        return df_desc
        
    def filter_out_embeddings_done(self, df_desc):
        collection_infos = self.chroma.collection.get()
        done_ids = collection_infos["ids"]
        df_desc = df_desc.loc[~df_desc[self.name.id_unique].isin(done_ids)]
        self._log.info(f"DONE IDS in CHROMA DB = {len(done_ids)}")
        return df_desc
