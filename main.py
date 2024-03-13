from src.context import get_config_context
from src.datacrawl.steps.step_crawler_met import StepCrawlingMet
from src.datacrawl.steps.step_crawler_drouot import StepCrawlingDrouot
from src.datacrawl.steps.step_text_clean import StepTextClean
from src.datacrawl.steps.step_text_embedding import StepTextEmbedding

if __name__ == "__main__":
    config, context = get_config_context('./configs', use_cache = False, save=False)

    # crawl = StepCrawlingDrouot(context=context, config=config, threads=4, object='chaise')
    # crawl.run(crawl.get_urls(), crawl.crawling_function)

    self = StepTextClean(context=context, config=config)
    df = self.run()

    import pandas as pd 
    df = pd.read_sql("DROUOT_202401", con=context.db_con)

    self = StepTextEmbedding(context=context, config=config)
    embed = self.run(df["DESCRIPTION"].tolist()[:10000])
   
    from sklearn.manifold import TSNE

    result = TSNE().fit_transform(embed)
    print(result.shape)  # (924, 2)