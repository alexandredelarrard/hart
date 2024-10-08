import click
from typing import List

from src.constants.command_line_interface import (
    CONFIG_ARGS,
    CONFIG_KWARGS,
    DATABASE_NAME_ARGS,
    DATABASE_NAME_KWARGS,
    SAVE_EMBEDDINGS_ARGS,
    SAVE_EMBEDDINGS_KWARGS,
    CRAWL_THREADS_ARG,
    CRAWL_THREADS_KWARG,
    OBJECT_ARGS,
    OBJECT_KWARGS,
    GPT_METHODE_ARGS,
    GPT_METHODE_KWARGS,
    INPUT_TYPE_ARGS,
    INPUT_TYPE_KWARGS,
)

from src.context import get_config_context
from src.utils.cli_helper import SpecialHelpOrder
from src.modelling.steps.step_text_clustering import StepTextClustering
from src.modelling.steps.step_fill_db_embeddings import StepFillDBEmbeddings
from src.modelling.steps.step_picture_classification import StepPictureClassification
from src.modelling.steps.step_gpt_text_inference import StepTextInferenceGpt


@click.group(cls=SpecialHelpOrder)
def cli():
    """
    HART PIPELINE STEPS
    """


@cli.command(
    help="embedding db of art house into chroma db embeddings",
    help_priority=1,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*DATABASE_NAME_ARGS, **DATABASE_NAME_KWARGS)
@click.option(*SAVE_EMBEDDINGS_ARGS, **SAVE_EMBEDDINGS_KWARGS)
def step_embed_art_house(config_path, database_name: str, save_embeddings: bool):

    config, context = get_config_context(config_path, use_cache=False, save=False)
    step_cluster = StepTextClustering(
        config=config,
        context=context,
        database_name=database_name,
        save_embeddings=save_embeddings,
    )

    # embeddings and saving for queries
    step_cluster.run()

    # python -m src modelling step-embed-art-house -tv DESCRIPTION -ah drouot


@cli.command(
    help="embedding db of art house into chroma db embeddings",
    help_priority=1,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*INPUT_TYPE_ARGS, **INPUT_TYPE_KWARGS)
def step_fill_db_embeddings(config_path, input_type):

    config, context = get_config_context(config_path, use_cache=False, save=False)
    enrich_chroma_picts = StepFillDBEmbeddings(
        config=config, context=context, type=input_type
    )

    # embeddings and saving for queries
    enrich_chroma_picts.run()

    # python -m src modelling step-fill-db-embeddings -inpt text_embedding_en


@cli.command(
    help="Extract Json from description with gpt3.5",
    help_priority=2,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
def step_train_picture_classification(config_path):

    config, context = get_config_context(config_path, use_cache=False, save=False)
    step_inference = StepPictureClassification(config=config, context=context)

    # get crawling_function
    step_inference.training()

    # python -m src modelling step-train-picture-classification


@cli.command(
    help="Extract Json from description with gpt3.5",
    help_priority=15,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
def step_predict_picture_classification(config_path):

    config, context = get_config_context(config_path, use_cache=False, save=False)
    step_inference = StepPictureClassification(config=config, context=context)

    # get crawling_function
    step_inference.predicting()

    # python -m src modelling step-predict-picture-classification


@cli.command(
    help="Extract Json from description with gpt3.5 or any other model like llama 3 8b",
    help_priority=2,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
@click.option(*OBJECT_ARGS, **OBJECT_KWARGS)
@click.option(*GPT_METHODE_ARGS, **GPT_METHODE_KWARGS)
def step_inference_gpt(config_path, threads: int, object: str, methode: str):

    config, context = get_config_context(config_path, use_cache=False, save=False)
    step_inference = StepTextInferenceGpt(
        config=config,
        context=context,
        threads=threads,
        object=object,
        methode=methode.split(","),
    )

    # get crawling_function
    step_inference.run()

    # python -m src modelling step-inference-gpt -t 10 --object ring --gpt-methode open_ai,groq,google
