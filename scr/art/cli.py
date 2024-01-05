import click 
import logging

from src.constants.command_line_interface import (
    CONFIG_ARGS,
    CONFIG_KWARGS,
    WEBPAGE_ARG,
    WEBPAGE_KWARG,
    CRAWL_THREADS_ARG, 
    CRAWL_THREADS_KWARG
)

from src.context import get_config_context
from src.utils.cli_helper import SpecialHelpOrder
from src.art.steps.step_crawler import Crawling

@click.group(cls=SpecialHelpOrder)
def cli():
    """
    HART PIPELINE STEPS
    """

@cli.command(
    help="Crawling pages",
    help_priority=1,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*WEBPAGE_ARG, **WEBPAGE_KWARG)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
def step_crawling(
    config_path, webpage_url : str, threads : int
):
    config, context = get_config_context(config_path, use_cache = False, save=False)

    crawl = Crawling(config, context, webpage_url, threads)
    crawl.run()