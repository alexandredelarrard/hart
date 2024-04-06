from src.context import get_config_context

from src.datacrawl.steps.step_crawler_met import StepCrawlingMet
from src.datacrawl.steps.step_crawler_drouot_items import StepCrawlingDrouotItems
from src.datacrawl.steps.step_crawler_christies_items import StepCrawlingChristiesItems
from src.datacrawl.steps.step_crawler_detailed import StepCrawlingDetailed
from src.datacrawl.steps.step_text_clean_drouot import StepTextCleanDrouot
from src.datacrawl.steps.step_text_clean_christies import StepTextCleanChristies
from src.datacrawl.steps.step_crawler_sothebys_auctions import StepCrawlingSothebysAuctions
from src.datacrawl.steps.step_crawler_sothebys_items import StepCrawlingSothebysItems
from src.datacrawl.steps.step_text_clean_sothebys import StepTextCleanSothebys
from src.datacrawl.steps.step_agglomerate_text_infos import StepAgglomerateTextInfos
from src.modelling.steps.step_text_clustering import StepTextClustering
from src.modelling.steps.step_manual_cluster import StepManualCluster
from src.modelling.steps.step_picture_classification import StepPictureClassification
from src.modelling.steps.step_text_inference_gpt import StepTextInferenceGpt
from src.modelling.steps.step_clean_gpt_inference import StepCleanGptInference

if __name__ == "__main__":

    config, context = get_config_context('./configs', use_cache = False, save=False)

    # self = StepTextCleanSothebys(context=context, config=config)
    # self.run()

    # self = StepCrawlingDetailed(context=context, config=config, threads=1, seller="drouot")

    # self = StepCrawlingDrouotItems(context=context, config=config, threads=4)
    # crawl.run(crawl.get_urls(), crawl.crawling_function)

    # self = StepCrawlingChristiesItems(context=context, config=config, threads=1)
    # self.run(self.get_auctions_urls_to_wrawl(), self.crawling_list_auctions_function)
    # self.run(self.get_list_items_to_crawl(), self.crawling_list_items_function)

    # self = StepTextCleanDrouot(context=context, config=config)
    # df = self.run()

    # self = StepTextCleanChristies(context=context, config=config)
    # embed = self.run()    

    # self = StepTextCleanSothebys(context=context, config=config)
    # embed = self.run()

    # self = StepTextClustering(context=context, config=config, database_name="all")
    # df_desc = self.run()

    # self = StepPictureClustering(context=context, config=config)
    # embed = self.run()

    # self = StepAgglomerateTextInfos(context=context, config=config)
    # df = self.run()

    # self = StepManualCluster(context=context, config=config, database_name="all")

    # self = StepPictureClassification(context=context, config=config, database_name="all")
    # self.training()

    # self = StepTextInferenceGpt(context=context, config=config)

    self = StepCleanGptInference(context=context, config=config)

