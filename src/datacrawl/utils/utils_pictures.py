from omegaconf import DictConfig
import os

from src.context import Context
from src.utils.step import Step 

class PicturesUtils(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):
        
        super().__init__(context=context, config=config)

    def get_pictures_url_drouot(self, df_details):
        df_details = df_details.explode(self.name.url_picture)
        df_details = df_details.loc[df_details[self.name.url_picture].notnull()]
        df_details[self.name.url_picture] = df_details[self.name.url_picture].apply(lambda x: 
                                                str(x).split("url(")[-1].split(")")[0].replace("\"", "").replace("size=small", "size=phare"))
        df_details[self.name.id_picture] = df_details[self.name.url_picture].apply(lambda x: os.path.basename(x))
        df_details = df_details.loc[df_details[self.name.url_picture] != "nan"]
        return df_details
    
    def get_pictures_url_christies(self, df_details):
        return df_details
    
    def get_pictures_url_sothebys(self, df_details):
        return df_details