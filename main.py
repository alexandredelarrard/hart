from src.context import get_config_context

from src.datacrawl.steps.step_crawl_artists import StepCrawlingArtists
from src.datacrawl.steps.step_crawl_pictures import StepCrawlingPictures
from src.datacrawl.steps.step_crawler_met import StepCrawlingMet
from src.datacrawl.steps.step_crawler_drouot_items import StepCrawlingDrouotItems
from src.datacrawl.steps.step_crawler_christies_items import StepCrawlingChristiesItems
from src.datacrawl.steps.step_crawler_detailed import StepCrawlingDetailed
from src.datacrawl.steps.step_text_clean_drouot import StepTextCleanDrouot
from src.datacrawl.steps.step_text_clean_christies import StepTextCleanChristies
from src.datacrawl.steps.step_crawler_sothebys_auctions import StepCrawlingSothebysAuctions
from src.datacrawl.steps.step_crawler_sothebys_items import StepCrawlingSothebysItems
from src.datacrawl.steps.step_text_clean_sothebys import StepTextCleanSothebys
from src.datacrawl.steps.step_text_clean_artists import StepTextCleanArtists
from src.datacrawl.steps.step_agglomerate_text_infos import StepAgglomerateTextInfos

from src.modelling.steps.step_text_clustering import StepTextClustering
from src.modelling.steps.step_picture_clustering import StepPictureClustering
from src.modelling.steps.old.step_manual_cluster import StepManualCluster
from src.modelling.steps.step_picture_classification import StepPictureClassification
from src.modelling.steps.step_gpt_text_inference import StepTextInferenceGpt
from src.modelling.steps.step_gpt_clean_inference import StepCleanGptInference
from src.modelling.steps.step_gbm_price_evaluator import StepGBMPriceEvaluator
from src.modelling.steps.step_knn_price_evaluator import StepKNNPriceEvaluator
from src.modelling.steps.step_text_classification import StepTextClassification
from src.modelling.steps.step_fill_chroma_pictures import StepFillChromaPictures

from src.modelling.transformers.TextModel import TextModel

if __name__ == "__main__":

    config, context = get_config_context('./configs', use_cache = False, save=False)

    # self = StepCrawlingArtists(context=context, config=config, threads=1)
    self = StepTextCleanArtists(context=context, config=config)

    # self = StepTextCleanSothebys(context=context, config=config)
    # self = StepCrawlingDetailed(context=context, config=config, threads=1, seller="drouot")

    # self = StepCrawlingDrouotItems(context=context, config=config, threads=4)
    # crawl.run(crawl.get_urls(), crawl.crawling_function)

    # self = StepCrawlingChristiesItems(context=context, config=config, threads=1)
    # self.run(self.get_auctions_urls_to_wrawl(), self.crawling_list_auctions_function)
    # self.run(self.get_list_items_to_crawl(), self.crawling_list_items_function)

    # self = StepCrawlingPictures(context=context, config=config, threads=1, seller="drouot")

    # self = StepTextCleanDrouot(context=context, config=config)
    # self.run()

    # self = StepTextCleanChristies(context=context, config=config)

    # self = StepTextCleanSothebys(context=context, config=config)
    # self.run()

    # self = StepTextClustering(context=context, config=config)

    # self = StepFillChromaPictures(context=context, config=config)

    # self = StepAgglomerateTextInfos(context=context, config=config)
    # self.run()

    # self = StepManualCluster(context=context, config=config, database_name="all")

    # self = StepPictureClassification(context=context, config=config)
    # self.predicting()

    # self = StepTextClassification(context=context, config=config)

    # self = StepTextInferenceGpt(context=context, config=config)

    # self = StepCleanGptInference(context=context, config=config)
    
    # self = StepGBMPriceEvaluator(context=context, config=config, category="vase")
    # self.training()

    # self = StepKNNPriceEvaluator(context=context, config=config, category="vase")

    # self = TextModel(context=context, config=config, model_name="meta-llama/Meta-Llama-3-8B-Instruct") #="D:/data/models/llm/Meta-Llama-3-8B-Instruct_fine_tuned_merged_model" "mistralai/Mistral-7B-Instruct-v0.2"