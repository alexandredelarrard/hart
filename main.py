from src.context import get_config_context

from src.datacrawl.steps.step_crawl_artists import StepCrawlingArtists
from src.datacrawl.steps.step_crawler_pictures import StepCrawlingPictures
from src.datacrawl.steps.step_crawler_met import StepCrawlingMet
from src.datacrawl.steps.step_crawler_detailed import StepCrawlingDetailed
from src.datacrawl.steps.step_crawler_items import StepCrawlingItems
from src.datacrawl.steps.step_crawler_auctions import StepCrawlingAuctions

from src.dataclean.steps.step_text_clean_crawling import StepCleanCrawling
from src.dataclean.steps.step_text_clean_artists import StepTextCleanArtists
from src.dataclean.steps.step_agglomerate_text_infos import StepAgglomerateTextInfos

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
from src.datacrawl.transformers.Crawling import Crawling

if __name__ == "__main__":

    config, context = get_config_context('./configs', use_cache = False, save=False)

    # self = StepCrawling(context=context, config=config, threads=1, text_only=True)
    # self = StepCrawlingArtists(context=context, config=config, threads=1)
    
    # self = StepCrawlingDetailed(context=context, config=config, threads=1, seller="christies", mode="new")
    # self = StepCrawlingAuctions(context=context, config=config, threads=1, seller="christies", start_date="2024-03-01", end_date="2024-05-01")
    # self = StepCrawlingItems(context=context, config=config, threads=1, seller="sothebys", mode="new")
    # self = StepCrawlingPictures(context=context, config=config, threads=1, seller="christies", mode="new")

    # self = StepCleanCrawling(context=context, config=config, seller="sothebys", mode="history")
    # self = StepTextCleanArtists(context=context, config=config)
    # self = StepAgglomerateTextInfos(context=context, config=config, mode="new")
    # self.run() 

    # self = StepTextClustering(context=context, config=config)
    self = StepFillChromaPictures(context=context, config=config)

    # self = StepManualCluster(context=context, config=config, database_name="all")

    # self = StepPictureClassification(context=context, config=config)
    # self = StepTextClassification(context=context, config=config)

    # self = StepTextInferenceGpt(context=context, config=config)
    # self = StepCleanGptInference(context=context, config=config)
    
    # self = StepGBMPriceEvaluator(context=context, config=config, category="vase")
    # self.training()

    # self = StepKNNPriceEvaluator(context=context, config=config, category="vase")
    # self = TextModel(context=context, config=config, model_name="meta-llama/Meta-Llama-3-8B-Instruct") #="D:/data/models/llm/Meta-Llama-3-8B-Instruct_fine_tuned_merged_model" "mistralai/Mistral-7B-Instruct-v0.2"