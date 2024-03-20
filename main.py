from src.context import get_config_context
from src.datacrawl.steps.step_crawler_met import StepCrawlingMet
from src.datacrawl.steps.step_crawler_drouot_items import StepCrawlingDrouotItems
from src.datacrawl.steps.step_crawler_christies_items import StepCrawlingChristiesItems
from src.datacrawl.steps.step_text_clean_drouot import StepTextCleanDrouot
from src.datacrawl.steps.step_text_clustering import StepTextClustering
from src.datacrawl.steps.step_text_clean_christies import StepTextCleanChristies
from src.datacrawl.steps.step_picture_clustering import StepPictureClustering
from src.datacrawl.steps.step_crawler_sothebys_auctions import StepCrawlingSothebysAuctions
from src.datacrawl.steps.step_crawler_sothebys_items import StepCrawlingSothebysItems


if __name__ == "__main__":
    config, context = get_config_context('./configs', use_cache = False, save=False)

    self = StepCrawlingSothebysItems(context=context, config=config, threads=1)

    # self = StepCrawlingDrouotItems(context=context, config=config, threads=4)
    # crawl.run(crawl.get_urls(), crawl.crawling_function)

    # self = StepCrawlingChristiesItems(context=context, config=config, threads=1)
    # self.run(self.get_auctions_urls_to_wrawl(), self.crawling_list_auctions_function)
    # self.run(self.get_list_items_to_crawl(), self.crawling_list_items_function)

    # self = StepTextCleanDrouot(context=context, config=config, seller="drouot")
    # df = self.run()

    # self = StepTextClustering(context=context, config=config)
    # embed = self.run()

    # self = StepPictureClustering(context=context, config=config)
    # embed = self.run()

    # self = StepTextCleanChristies(context=context, config=config)
    # embed = self.run()
