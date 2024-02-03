import click 

from src.constants.command_line_interface import (
    CONFIG_ARGS,
    CONFIG_KWARGS,
    WEBPAGE_ARG,
    WEBPAGE_KWARG,
    OBJECT_ARGS,
    OBJECT_KWARGS,
    CRAWL_THREADS_ARG, 
    CRAWL_THREADS_KWARG
)

from src.context import get_config_context
from src.utils.cli_helper import SpecialHelpOrder
from src.art.steps.step_crawler_met import StepCrawlingMet
from src.art.steps.step_crawler_drouot import StepCrawlingDrouot 
from src.art.steps.step_crawler_chrysties import StepCrawlingChristies


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
    help="Crawling DROUOT",
    help_priority=3,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*OBJECT_ARGS, **OBJECT_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
def step_crawling_drouot(
    config_path, threads : int, object : str 
):
    
    config, context = get_config_context(config_path, use_cache = False, save=False)
    crawl = StepCrawlingDrouot(config=config, context=context, threads=threads, object=object)

    # get crawling_function 
    crawl.run(crawl.get_urls(), crawl.crawling_function)

    #python -m src art step-crawling-drouot -obj meuble -t 1


@cli.command(
    help="Crawling DROUOT",
    help_priority=3,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*OBJECT_ARGS, **OBJECT_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
def step_crawling_christies(
    config_path, threads : int, object : str 
):
    
    config, context = get_config_context(config_path, use_cache = False, save=False)
    crawl = StepCrawlingChristies(config=config, context=context, threads=threads, object=object)

    # get crawling_function 
    crawl.run(crawl.get_urls(), crawl.crawling_function)

    #python -m src art step-crawling-drouot -obj meuble -t 1

