from omegaconf import DictConfig

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling
from src.utils.utils_crawler import (read_crawled_csvs, 
                                    read_crawled_pickles,
                                    keep_files_to_do,
                                    define_save_paths)

class StepCrawlingDetailed(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int,
                 seller : str = "christies",
                 save_queue_size : int = 500,
                 text_only : bool = True,
                 mode: str= "history"):

        super().__init__(context=context, config=config, threads=threads, 
                         text_only=text_only, save_in_queue=True, 
                         save_queue_size_step=save_queue_size)

        self.seller = seller
        self.paths = define_save_paths(config, self.seller, mode=mode)

        self.recrawl_pictures = False
        self.per_element = self._config.crawling[self.seller].detailed.per_element
    
    # second crawling step  to get list of pieces per auction 
    def get_list_items_to_crawl(self):

        # get detail urls to crawl
        df = read_crawled_csvs(path=self.paths["infos"])
        to_crawl = df.loc[df[self.name.url_full_detail].notnull(), 
                            self.name.url_full_detail].drop_duplicates().tolist()
        
        # get already crawled urls 
        df_crawled = read_crawled_pickles(path=self.paths["details"])
        if df_crawled.shape[0] != 0:
            if self.recrawl_pictures:
                df_crawled = df_crawled.loc[df_crawled[self.name.url_picture].notnull()]
            already_crawled = df_crawled[self.name.url_detail].tolist()
        else:
            already_crawled = []

        liste_urls = keep_files_to_do(to_crawl, already_crawled)
        return liste_urls
    
    def crawling_details_function(self, driver):

        infos = {self.name.url_detail : driver.current_url}
        for step, step_values in self.per_element.items(): 

            if "liste_elements" in step_values.keys():
                if "per_element" not in step_values.keys():
                    raise Exception("extraction of list needs to understand what to extract per element. Please add it to config")

                infos[step] = []
                liste_elements = self.get_elements(driver, 
                                    step_values.liste_elements["by_type"], 
                                    step_values.liste_elements["value_css"])
                for element in liste_elements:
                    infos[step].append(self.get_info_from_step_value(element, step_values.per_element))

            else:
                infos[step] =  self.get_info_from_step_value(driver, step_values)
        
        return driver, infos