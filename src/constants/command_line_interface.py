import click

from src.utils.cli_helper import (
    assert_valid_url
)

CONFIG_ARGS = ("--config", "-c", "config_path")
CONFIG_KWARGS = {
    "default" : "./configs",
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


DATABASE_NAME_ARGS=("--house_art", "-ah", "database_name")
DATABASE_NAME_KWARGS= {
    "type" : str, 
    "default" : "drouot",
    "required" : True,
    "show_default" : True,
    "help": (
        "house of the dabase drouot, christies, etc."
    )
}

TEXT_VECTOR_ARGS=("--text_vector", "-tv", "vector")
TEXT_VECTOR_KWARGS= {
    "type" : str, 
    "default" : "DESCRIPTION",
    "required" : True,
    "show_default" : True,
    "help": (
        "feature from the database to embed and query from"
    )
}


TEXT_ONLY_ARGS=("--text-only", "-to", "text_only")
TEXT_ONLY_KWARGS= {
    "type" : bool, 
    "default" : True, 
    "required" : False,
    "show_default" : True,
    "help": (
        "if we want to initialize the webdriver without loading javascript / images etc. for fast crawling"
    )
}

SELLER_ARGS=("--seller", "-s", "seller")
SELLER_KWARGS= {
    "type" : str, 
    "default" : "christies", 
    "required" : True,
    "show_default" : True,
    "help": (
        "seller, either drouot, christies or sothebys"
    )
}

QUEUE_SIZE_ARGS=("--save-queue-size", "-sqs", "save_queue_size")
QUEUE_SIZE_KWARGS= {
    "type" : int, 
    "default" : 500, 
    "required" : False,
    "show_default" : True,
    "help": (
        "when save from queue, size of number of elements in queue so trigger save"
    )
}

SAVE_EMBEDDINGS_ARGS=("--save-embeddings", "-semb", "save_embeddings")
SAVE_EMBEDDINGS_KWARGS={
    "type" : bool, 
    "default" : True, 
    "required" : False,
    "show_default" : True,
    "help": (
        "save embeddings or not into a chroma db for futur similarity calculation"
    )
}

GPT_METHODE_ARGS=("--gpt-methode", "-gptm", "methode")
GPT_METHODE_KWARGS={
    "type" : str, 
    "default" : "local", 
    "required" : True,
    "show_default" : "local",
    "help": (
        "which api to call for llm inference based on text. If local, need to start local server first with LM Studio"
    )
}

START_DATE_ARGS=("--start-date", "-sd", "start_date")
START_DATE_KWARGS= {
    "type" : str, 
    "default" : None,
    "required" : False,
    "show_default" : True,
    "help": (
        "Start date from which to crawl auctions from a defined website"
    )
}

END_DATE_ARGS=("--end-date", "-ed", "end_date")
END_DATE_KWARGS= {
    "type" : str, 
    "default" : None,
    "required" : False,
    "show_default" : True,
    "help": (
        "End date from which to crawl auctions from a defined website"
    )
}

CRAWLING_MODE_ARGS=("--crawling-mode", "-crm", "crawling_mode")
CRAWLING_MODE_KWARGS= {
    "type" : str, 
    "default" : "history",
    "required" : False,
    "show_default" : True,
    "help": (
        "Either history or new depending if want to crawl all or append to existing values"
    )
}

OBJECT_ARGS=("--object", "-obj", "object")
OBJECT_KWARGS= {
    "type" : str, 
    "default" : None,
    "required" : False,
    "show_default" : True,
    "help": (
        "Kind of art object to create embedding & co"
    )
}