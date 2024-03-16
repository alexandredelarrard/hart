from src.context import get_config_context
from src.datacrawl.steps.step_crawler_met import StepCrawlingMet
from src.datacrawl.steps.step_crawler_drouot import StepCrawlingDrouot
from src.datacrawl.steps.step_crawler_christies import StepCrawlingChristies
from src.datacrawl.steps.step_text_clean import StepTextClean
from src.datacrawl.steps.step_text_clustering import StepTextClustering
from src.datacrawl.steps.step_picture_clustering import StepPictureClustering

if __name__ == "__main__":
    config, context = get_config_context('./configs', use_cache = False, save=False)

    # crawl = StepCrawlingDrouot(context=context, config=config, threads=4, object='chaise')
    # crawl.run(crawl.get_urls(), crawl.crawling_function)

    self = StepCrawlingChristies(context=context, config=config, threads=1)
    # self.run(self.get_auctions_urls_to_wrawl(), self.crawling_list_auctions_function)
    self.run(self.get_list_items_to_crawl(), self.crawling_list_items_function)

    # self = StepTextClean(context=context, config=config, seller="drouot")
    # df = self.run()

    # self = StepTextClustering(context=context, config=config)
    # embed = self.run()

    # self = StepPictureClustering(context=context, config=config)
    # embed = self.run()