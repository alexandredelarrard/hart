from src.context import get_config_context
from src.art.steps.step_crawler_met import StepCrawlingMet
from src.art.steps.step_crawler_drouot import StepCrawlingDrouot

if __name__ == "__main__":
    config, context = get_config_context('./configs', use_cache = False, save=False)

    crawl = StepCrawlingDrouot(context=context, config=config, threads=4, object='chaise')
    crawl.run(crawl.get_urls(), crawl.crawling_function)

    df_m = pd.read_csv(config.flat_file.insee.carreaux_200.met)
    code_geo = pd.read_csv(config.flat_file.insee.communes_encodage)