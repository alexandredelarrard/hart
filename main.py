from src.context import get_config_context
from src.datacrawl.steps.step_crawler_met import StepCrawlingMet
from src.datacrawl.steps.step_crawler_drouot import StepCrawlingDrouot
from src.datacrawl.steps.step_text_clean import StepTextClean

if __name__ == "__main__":
    config, context = get_config_context('./configs', use_cache = False, save=False)

    # crawl = StepCrawlingDrouot(context=context, config=config, threads=4, object='chaise')
    # crawl.run(crawl.get_urls(), crawl.crawling_function)

    step_clean = StepTextClean(context=context, config=config)
    step_clean.run()