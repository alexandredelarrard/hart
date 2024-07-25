import click

from src.constants.command_line_interface import (
    CONFIG_ARGS,
    CONFIG_KWARGS,
    CRAWL_THREADS_ARG,
    CRAWL_THREADS_KWARG,
    TEXT_ONLY_ARGS,
    TEXT_ONLY_KWARGS,
    SELLER_ARGS,
    SELLER_KWARGS,
    QUEUE_SIZE_ARGS,
    QUEUE_SIZE_KWARGS,
    START_DATE_ARGS,
    START_DATE_KWARGS,
    END_DATE_ARGS,
    END_DATE_KWARGS,
    CRAWLING_MODE_ARGS,
    CRAWLING_MODE_KWARGS,
)

from src.context import get_config_context
from src.utils.cli_helper import SpecialHelpOrder
from src.datacrawl.steps.step_crawler_met import StepCrawlingMet
from src.datacrawl.steps.step_crawl_artists import StepCrawlingArtists
from src.datacrawl.steps.step_crawler_items import StepCrawlingItems
from src.datacrawl.steps.step_crawler_auctions import StepCrawlingAuctions
from src.datacrawl.steps.step_crawler_details import StepCrawlingDetails
from src.datacrawl.steps.step_crawler_pictures import StepCrawlingPictures


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
def step_crawling_met(config_path, threads: int):

    config, context = get_config_context(config_path, use_cache=False, save=False)
    crawl = StepCrawlingMet(config=config, context=context, threads=threads)

    # get crawling_function
    crawl.run(crawl.get_urls(config), crawl.crawling_function)

    # python -m src art step-crawling -t 1


@cli.command(
    help="Crawling AUCTIONS for any seller",
    help_priority=3,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
@click.option(*SELLER_ARGS, **SELLER_KWARGS)
@click.option(*START_DATE_ARGS, **START_DATE_KWARGS)
@click.option(*END_DATE_ARGS, **END_DATE_KWARGS)
def step_crawling_auctions(
    config_path,
    threads: int,
    seller: str,
    start_date: str,
    end_date: str,
):

    config, context = get_config_context(config_path, use_cache=False, save=False)
    crawl = StepCrawlingAuctions(
        config=config,
        context=context,
        threads=threads,
        seller=seller,
        start_date=start_date,
        end_date=end_date,
    )

    # get crawling_function
    crawl.run(crawl.get_auctions_urls_to_crawl(), crawl.crawling_auctions_iteratively)

    # python -m src datacrawl step-crawling-auctions -t 1 --seller sothebys --start-date "2024-03-01"


@cli.command(
    help="Crawling ITEMS for any seller",
    help_priority=3,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
@click.option(*SELLER_ARGS, **SELLER_KWARGS)
def step_crawling_items(config_path, threads: int, seller: str):

    config, context = get_config_context(config_path, use_cache=False, save=False)
    crawl = StepCrawlingItems(
        config=config,
        context=context,
        threads=threads,
        seller=seller,
    )

    # get crawling_function
    crawl.run(crawl.get_list_items_to_crawl(), crawl.crawl_items_iteratively)

    # python -m src datacrawl step-crawling-items -t 1 --seller sothebys --crawling-mode new


@cli.command(
    help="Crawling details for any seller",
    help_priority=6,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*SELLER_ARGS, **SELLER_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
def step_crawling_details(config_path, threads: int, seller: str):

    config, context = get_config_context(config_path, use_cache=False, save=False)
    crawl = StepCrawlingDetails(
        config=config,
        context=context,
        threads=threads,
        seller=seller,
    )

    crawl.run(crawl.get_list_items_to_crawl(), crawl.crawling_details_function)
    # python -m src datacrawl step-crawling-details -t 1 -s christies


@cli.command(
    help="Crawling Pictures for any seller",
    help_priority=5,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*SELLER_ARGS, **SELLER_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
@click.option(*CRAWLING_MODE_ARGS, **CRAWLING_MODE_KWARGS)
def step_crawling_pictures(config_path, threads: int, seller: str, crawling_mode: str):

    config, context = get_config_context(config_path, use_cache=False, save=False)
    crawl = StepCrawlingPictures(
        config=config,
        context=context,
        threads=threads,
        seller=seller,
        mode=crawling_mode,
    )

    # get crawling_function
    crawl.run(crawl.get_list_items_to_crawl(), crawl.crawling_picture)

    if seller == "drouot":
        crawl.run(crawl.get_list_items_to_crawl(mode="canvas"), crawl.crawling_canvas)

    # python -m src datacrawl step-crawling-pictures -t 5 --seller drouot


@cli.command(
    help="Crawling Artist list",
    help_priority=5,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
def step_crawling_artists(config_path, threads: int):

    config, context = get_config_context(config_path, use_cache=False, save=False)
    crawl = StepCrawlingArtists(config=config, context=context, threads=threads)

    # get crawling_function
    crawl.run(crawl.get_list_items_to_crawl(), crawl.crawling_artists)
    # python -m src datacrawl step-crawling-artists -t 1
