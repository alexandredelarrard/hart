from src.context import Context
from src.dataclean.transformers.TextCleaner import TextCleaner
from src.utils.timing import timing

from src.dataclean.utils.utils_clean_christies import CleanChristies
from src.dataclean.utils.utils_clean_drouot import CleanDrouot
from src.dataclean.utils.utils_clean_sothebys import CleanSothebys
from src.dataclean.utils.utils_clean_millon import CleanMillon

from src.utils.utils_crawler import (read_crawled_csvs,
                                     read_crawled_pickles,
                                     define_save_paths)

from omegaconf import DictConfig


class StepCleanCrawling(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 seller: str,
                 mode: str = "history"):

        super().__init__(context=context, config=config)

        self.seller = seller
        self.paths = define_save_paths(config, self.seller, mode=mode)
        self.webpage_url = self._config.crawling[self.seller].webpage_url

        self.details_col_names = self.name.dict_rename_detail()
        self.items_col_names= self.name.dict_rename_items()
        self.auctions_col_names= self.name.dict_rename_auctions()
        
        self.sql_table_name = self.get_sql_db_name(self.seller, mode)
        self.seller_utils = eval(f"Clean{self.seller.capitalize()}(context=context, config=config)")
        

    @timing
    def run(self):
        
        # CLEAN AUCTIONS
        df_auctions = read_crawled_csvs(path=self.paths["auctions"])
        df_auctions = self.renaming_dataframe(df_auctions, mapping_names=self.auctions_col_names)
        df_auctions = self.seller_utils.clean_auctions(df_auctions)
        df_auctions = df_auctions.loc[df_auctions[self.name.id_auction]!="MISSING_URL_AUCTION"]

        # # CLEAN ITEMS
        df = read_crawled_csvs(path=self.paths["infos"])
        df = self.renaming_dataframe(df, mapping_names=self.items_col_names)
        df = self.seller_utils.clean_items_per_auction(df)
        df = self.extract_estimates(df) # text cleaner
        df = self.extract_currency(df) # text cleaner
        df = self.add_complementary_variables(df, self.seller) # text cleaner
        df = self.clean_estimations(df, ["this lot has been withdrawn from auction", 
                                        "estimate on request", 
                                        "estimate unknown",
                                        "price realised", 
                                        "résultat : non communiqué", 
                                        'estimation : manquante']) # text cleaner
        df = self.remove_missing_values(df) # text cleaner
        df = self.extract_infos(df) # text cleaner

        # CLEAN DETAILED ITEM DATA
        df_detailed = read_crawled_pickles(path=self.paths["details"])
        df_detailed = self.renaming_dataframe(df_detailed, mapping_names=self.details_col_names)
        df_detailed = self.clean_detail_infos(df_detailed)
        df_detailed = self.remove_features(df_detailed, ["NOTE_CATALOGUE", 
                                                         "ARTIST"])

        # MERGE DETAILED ITEM DATA 
        df = self.concatenate_detail(df, df_detailed)
        df = self.seller_utils.explode_df_per_picture(df)
        df = self.clean_id_picture(df, seller=self.seller)

        #MERGE ITEM & AUCTIONS
        df = self.concatenate_auctions(df, df_auctions)
        df = self.remove_features(df, [self.name.item_infos, 
                                        self.name.brut_estimate, 
                                        self.name.brut_result,
                                        self.name.detail_file,
                                        self.name.item_title, 
                                        self.name.item_file,
                                        self.name.url_picture + "_DETAIL",
                                        self.name.auction_file,
                                        self.name.date + "_AUCTION",
                                        self.name.auction_title + "_AUCTION",
                                        self.name.url_auction + "_AUCTION",
                                        self.name.place + "_AUCTION",
                                        self.name.house + "_AUCTION",
                                        self.name.type_sale + "_AUCTION"])
        df = df.drop_duplicates(self.name.url_full_detail)
    
        # SAVE ITEMS ENRICHED
        self.write_sql_data(dataframe=df,
                            table_name=self.sql_table_name,
                            if_exists="replace")
        
        return df
