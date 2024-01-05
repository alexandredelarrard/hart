import click

from src.utils.cli_helper import (
    assert_valid_url
)

CONFIG_ARGS = ("--config", "-c", "config_path")
CONFIG_KWARGS = {
    "default" : "config/",
    "show_default" : True,
    "help": (
        "The path to the configuration folder for the run. "
        "The config is recursively created or merged with the help of Omegaconf python lib"
    )
}

WEBPAGE_ARG = ("--webpage", "-wp", "webpage_url")
WEBPAGE_KWARG = {
    "type" : str,
    "default" : "https://www.gazette-drouot.com/",
    "show_default" : True,
    "required" : True,
    "help": (
        "The URL to retrieve infos from"
    ),
    "callback" : assert_valid_url,
}

CRAWL_THREADS_ARG =("--threads", "-t", "threads")
CRAWL_THREADS_KWARG = {
    "type" : int, 
    "default" : 1,
    "required" : False,
    "show_default" : True,
    "help": (
        "The number of threads to run in parallel to crawl infos"
    )
}