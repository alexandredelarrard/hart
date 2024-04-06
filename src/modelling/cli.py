
import click 

from src.constants.command_line_interface import (
    CONFIG_ARGS,
    CONFIG_KWARGS,
    DATABASE_NAME_ARGS,
    DATABASE_NAME_KWARGS,
    SAVE_EMBEDDINGS_ARGS,
    SAVE_EMBEDDINGS_KWARGS,
    CRAWL_THREADS_ARG, 
    CRAWL_THREADS_KWARG,
    QUEUE_SIZE_ARGS,
    QUEUE_SIZE_KWARGS,
)

from src.context import get_config_context
from src.utils.cli_helper import SpecialHelpOrder
from src.modelling.steps.step_text_clustering import StepTextClustering
from src.modelling.steps.step_picture_classification import StepPictureClassification
from src.modelling.steps.step_text_inference_gpt import StepTextInferenceGpt
from src.modelling.steps.step_clean_gpt_inference import StepCleanGptInference

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
def step_embed_art_house(
    config_path, database_name : str, save_embeddings : bool 
):
    
    config, context = get_config_context(config_path, use_cache = False, save=False)
    step_cluster = StepTextClustering(config=config, context=context, 
                                      database_name=database_name,
                                      save_embeddings=save_embeddings)

    # embeddings and saving for queries 
    step_cluster.run()
    
    #python -m src modelling step-embed-art-house -tv DESCRIPTION -ah drouot

@cli.command(
    help="Extract Json from description with gpt3.5",
    help_priority=2,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
def step_train_picture_classification(
    config_path
):
    
    config, context = get_config_context(config_path, use_cache = False, save=False)
    step_inference = StepPictureClassification(config=config, context=context)

    # get crawling_function 
    step_inference.training()

    #python -m src modelling step-train-picture-classification
    

@cli.command(
    help="Extract Json from description with gpt3.5",
    help_priority=2,
)
@click.option(*CONFIG_ARGS, **CONFIG_KWARGS)
@click.option(*QUEUE_SIZE_ARGS, **QUEUE_SIZE_KWARGS)
@click.option(*CRAWL_THREADS_ARG, **CRAWL_THREADS_KWARG)
def step_inference_gpt(
    config_path, threads : int, save_queue_size : int,
):
    
    config, context = get_config_context(config_path, use_cache = False, save=False)
    step_inference = StepTextInferenceGpt(config=config, context=context, 
                                          threads=threads, 
                                          save_queue_size=save_queue_size)

    # get crawling_function 
    step_inference.run()

    #python -m src modelling step-inference-gpt -t 6 -sqs 50
    
