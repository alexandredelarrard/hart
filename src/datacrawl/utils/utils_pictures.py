from omegaconf import DictConfig
import os

from src.context import Context
from src.utils.step import Step 
from src.utils.utils_crawler import encode_file_name
from src.dataclean.utils.utils_clean_drouot import clean_url_picture_list

class PicturesUtils(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):
        
        super().__init__(context=context, config=config)

    def get_pictures_url_drouot(self, df_details, mode):

        if mode != "canvas":
            df_details = df_details.explode(self.name.url_picture)
            df_details = df_details.loc[df_details[self.name.url_picture].notnull()]
            df_details[self.name.url_picture] = df_details[self.name.url_picture].apply(lambda x: clean_url_picture_list(x))
            df_details[self.name.id_picture] = df_details[self.name.url_picture].apply(lambda x: os.path.basename(x))
            df_details = df_details.loc[df_details[self.name.url_picture] != "nan"]
        else:
            df_details = df_details.drop_duplicates("CURRENT_URL")
            df_details = df_details.loc[df_details[self.name.url_picture].isin([[]])]
            df_details[self.name.id_picture] = df_details["CURRENT_URL"].apply(lambda x: encode_file_name(os.path.basename(x)))
            df_details[self.name.url_picture] = df_details["CURRENT_URL"]

        return df_details[[self.name.id_picture, self.name.url_picture]]
    
    def get_pictures_url_christies(self, df_details, mode):
        return df_details
    
    def get_pictures_url_sothebys(self, df_details, mode):
        return df_details