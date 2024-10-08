from src.context import get_config_context

from src.datacrawl.steps.step_crawl_artists import StepCrawlingArtists
from src.datacrawl.steps.step_crawler_pictures import StepCrawlingPictures
from src.datacrawl.steps.step_crawler_met import StepCrawlingMet
from src.datacrawl.steps.step_crawler_details import StepCrawlingDetails
from src.datacrawl.steps.step_crawler_items import StepCrawlingItems
from src.datacrawl.steps.step_crawler_auctions import StepCrawlingAuctions

from src.dataclean.steps.step_text_clean_crawling import StepCleanCrawling
from src.dataclean.steps.step_text_clean_artists import StepTextCleanArtists
from src.dataclean.steps.step_gpt_clean_inference import StepCleanGptInference

from src.modelling.steps.step_gpt_text_inference import StepTextInferenceGpt
from src.modelling.steps.step_text_clustering import StepTextClustering
from src.modelling.steps.step_picture_clustering import StepPictureClustering
from src.modelling.steps.old.step_manual_cluster import StepManualCluster
from src.modelling.steps.step_picture_classification import StepPictureClassification
from src.modelling.steps.step_gbm_price_evaluator import StepGBMPriceEvaluator
from src.modelling.steps.step_knn_price_evaluator import StepKNNPriceEvaluator
from src.modelling.steps.step_text_classification import StepTextClassification
from src.modelling.steps.step_fill_db_embeddings import StepFillDBEmbeddings

from src.modelling.transformers.TextModel import TextModel
from src.datacrawl.transformers.Crawling import Crawling

from src.constants.variables import TEXT_DB_FR, TEXT_DB_EN, PICTURE_DB

if __name__ == "__main__":

    config, context = get_config_context("./configs", use_cache=False, save=False)

    # self = StepCrawlingArtists(context=context, config=config, threads=1)

    # self = StepCrawlingDetails(context=context, config=config, threads=1, seller="drouot")
    # self = StepCrawlingAuctions(
    #     context=context, config=config, threads=1, seller="millon"
    # )
    self = StepCrawlingItems(context=context, config=config, threads=1, seller="drouot")
    # self = StepCrawlingPictures(context=context, config=config, threads=1, seller="christies")

    # self = StepCleanCrawling(context=context, config=config)
    # self = StepTextCleanArtists(context=context, config=config)
    # self.run()

    # self = StepTextClustering(context=context, config=config)
    # self = StepPictureClustering(context=context, config=config)
    # self = StepFillDBEmbeddings(context=context, config=config, type=TEXT_DB_EN)

    # self = StepManualCluster(context=context, config=config, database_name="all")

    # self = StepPictureClassification(context=context, config=config)
    # self = StepTextClassification(context=context, config=config)

    # self = StepTextInferenceGpt(
    #     context=context, config=config, methode=["open_ai"], object="ring"
    # )
    # self = StepCleanGptInference(context=context, config=config, object="reformulate")
    # self = StepCategoryGptInference(context=context, config=config)
    # self.run()

    # self = StepGBMPriceEvaluator(context=context, config=config, category="vase")
    # self.training()

    # self = StepKNNPriceEvaluator(context=context, config=config, category="vase")
    # self = TextModel(context=context, config=config, model_name="meta-llama/Meta-Llama-3-8B-Instruct") #="D:/data/models/llm/Meta-Llama-3-8B-Instruct_fine_tuned_merged_model" "mistralai/Mistral-7B-Instruct-v0.2"
