import click 

from src.constants.command_line_interface import (
    CONFIG_ARGS,
    CONFIG_KWARGS,
    OBJECT_ARGS,
    OBJECT_KWARGS,
    CRAWL_THREADS_ARG, 
    CRAWL_THREADS_KWARG,
    DATABASE_NAME_ARGS,
    DATABASE_NAME_KWARGS,
    NBR_AUCTION_PAGES_ARGS,
    NBR_AUCTION_PAGES_KWARGS,
    TEXT_ONLY_ARGS,
    TEXT_ONLY_KWARGS,
    SELLER_ARGS,
    SELLER_KWARGS,
    QUEUE_SIZE_ARGS,
    QUEUE_SIZE_KWARGS,
    SAVE_EMBEDDINGS_ARGS,
    SAVE_EMBEDDINGS_KWARGS
)

from src.context import get_config_context
from src.utils.cli_helper import SpecialHelpOrder
from src.datacrawl.steps.step_crawler_met import StepCrawlingMet
from src.datacrawl.steps.step_crawler_drouot_items import StepCrawlingDrouotItems 
from src.datacrawl.steps.step_crawler_christies_items import StepCrawlingChristiesItems
from src.datacrawl.steps.step_crawler_drouot_auctions import StepCrawlingDrouotAuctions 
from src.datacrawl.steps.step_crawler_christies_auctions import StepCrawlingChristiesAuctions
from src.datacrawl.steps.step_crawler_sothebys_auctions import StepCrawlingSothebysAuctions
from src.datacrawl.steps.step_crawler_sothebys_items import StepCrawlingSothebysItems
from src.datacrawl.steps.step_text_clustering import StepTextClustering
from src.datacrawl.steps.step_crawler_detailed import StepCrawlingDetailed


@click.group(cls=SpecialHelpOrder)
def cli():
    """
    HART PIPELINE STEPS
    """


@cli.command(
    help="Crawling MET",
    help_priority=2,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
def step_crawling_met(
    config_path, threads : int 
):
    
    config, context = get_config_context(config_path, use_cache = False, save=False)
    crawl = StepCrawlingMet(config=config, context=context, threads=threads)

    # get crawling_function 
    crawl.run(crawl.get_urls(config), crawl.crawling_function)

    #python -m src art step-crawling -t 1


@cli.command(
    help="Crawling DROUOT AUCTIONS",
    help_priority=3,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
@click.option(*NBR_AUCTION_PAGES_ARGS, **NBR_AUCTION_PAGES_KWARGS)
def step_crawling_drouot_auctions(
    config_path, threads : int, nbr_auction_pages : int 
):
    
    config, context = get_config_context(config_path, use_cache = False, save=False)
    crawl = StepCrawlingDrouotAuctions(config=config, context=context, 
                                       threads=threads, 
                                       nbr_auction_pages=nbr_auction_pages)

    # get crawling_function 
    crawl.run(crawl.get_auctions_urls_to_wrawl(), crawl.crawling_list_auctions_function)

    #python -m src datacrawl step-crawling-drouot-auctions -t 1

@cli.command(
    help="Crawling SOTHEBYS AUCTIONS",
    help_priority=3,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
@click.option(*NBR_AUCTION_PAGES_ARGS, **NBR_AUCTION_PAGES_KWARGS)
def step_crawling_sothebys_auctions(
    config_path, threads : int, nbr_auction_pages : int 
):
    
    config, context = get_config_context(config_path, use_cache = False, save=False)
    crawl = StepCrawlingSothebysAuctions(config=config, context=context, 
                                       threads=threads)

    # get crawling_function 
    crawl.run(crawl.get_auctions_urls_to_wrawl(), crawl.crawling_list_auctions_function)

    #python -m src datacrawl step-crawling-sothebys-auctions -t 1

@cli.command(
    help="Crawling Chrysties Auctions",
    help_priority=3,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
def step_crawling_chrysties_auctions(
    config_path, threads : int
):
    
    config, context = get_config_context(config_path, use_cache = False, save=False)
    crawl = StepCrawlingChristiesAuctions(config=config, context=context, 
                                            threads=threads)

    # get crawling_function 
    crawl.run(crawl.get_auctions_urls_to_wrawl(), 
              crawl.crawling_list_auctions_function)
    #python -m src datacrawl step-crawling-chrysties-auctions -t 1


@cli.command(
    help="Crawling DROUOT ITEMS",
    help_priority=3,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*OBJECT_ARGS, **OBJECT_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
def step_crawling_drouot_items(
    config_path, threads : int, object : str 
):
    
    config, context = get_config_context(config_path, use_cache = False, save=False)
    crawl = StepCrawlingDrouotItems(config=config, context=context, 
                                    threads=threads, object=object)

    # get crawling_function 
    crawl.run(crawl.get_urls(), crawl.crawling_function)

    #python -m src datacrawl step-crawling-drouot-items -t 1


@cli.command(
    help="Crawling Chrysties",
    help_priority=4,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
def step_crawling_chrysties_items(
    config_path, threads : int
):
    
    config, context = get_config_context(config_path, use_cache = False, save=False)
    crawl = StepCrawlingChristiesItems(config=config, context=context, 
                                        threads=threads)

    # get crawling_function 
    crawl.run(crawl.get_list_items_to_crawl(), crawl.crawling_list_items_function)
    #python -m src datacrawl step-crawling-chrysties-items -t 1

@cli.command(
    help="Crawling Chrysties",
    help_priority=5,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
def step_crawling_sothebys_items(
    config_path, threads : int
):
    
    config, context = get_config_context(config_path, use_cache = False, save=False)
    crawl = StepCrawlingSothebysItems(config=config, context=context, 
                                        threads=threads)

    # get crawling_function 
    crawl.run(crawl.get_list_items_to_crawl(), crawl.crawling_list_items_function)
    #python -m src datacrawl step-crawling-sothebys-items -t 1 


@cli.command(
    help="Crawling detail of url",
    help_priority=6,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*SELLER_ARGS, **SELLER_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
@click.option(*QUEUE_SIZE_ARGS, **QUEUE_SIZE_KWARGS)
@click.option(*TEXT_ONLY_ARGS, **TEXT_ONLY_KWARGS)
def step_crawling_detailed(
    config_path, threads : int, seller : str, save_queue_size : int, text_only : bool
):
    
    config, context = get_config_context(config_path, use_cache = False, save=False)
    crawl = StepCrawlingDetailed(config=config, context=context, 
                                threads=threads, seller=seller, 
                                save_queue_size=save_queue_size,
                                text_only=text_only)

    crawl.run(crawl.get_list_items_to_crawl(), crawl.crawling_details_function)
    # python -m src datacrawl step-crawling-detailed -t 5 -s drouot -sqs 500 -to True


@cli.command(
    help="embedding db of art house into chroma db embeddings",
    help_priority=10,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*DATABASE_NAME_ARGS, **DATABASE_NAME_KWARGS)
@click.option(*SAVE_EMBEDDINGS_ARGS, **SAVE_EMBEDDINGS_KWARGS)
def step_embed_art_house(
    config_path, database_name : str, save_embeddings : bool 
):
    
    config, context = get_config_context(config_path, use_cache = False, save=False)
    step_cluster = StepTextClustering(config=config, context=context, 
                                      database_name=database_name,
                                      save_embeddings=save_embeddings)

    # embeddings and saving for queries 
    step_cluster.run()
    
    #python -m src art step-embed-art-house -tv DESCRIPTION -ah drouot
