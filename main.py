from src.context import get_config_context
from src.art.steps.step_crawler_met import StepCrawlingMet
from src.art.steps.step_crawler_drouot import StepCrawlingDrouot


if __name__ == "__main__":
    config, context = get_config_context('./configs', use_cache = False, save=False)

    crawl = StepCrawlingDrouot(context=context, config=config, threads=1, object='meuble')

    l = crawl.get_urls()

    # driver = crawl.initialize_driver_chrome()
    # driver.get(crawl.root_url + "&page=1")
    # driver = crawl.check_loggedin(driver)

    crawl.run(crawl.get_urls(), crawl.crawling_function)