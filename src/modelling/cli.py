
import click 

from src.constants.command_line_interface import (
    CONFIG_ARGS,
    CONFIG_KWARGS,
    DATABASE_NAME_ARGS,
    DATABASE_NAME_KWARGS,
    SAVE_EMBEDDINGS_ARGS,
    SAVE_EMBEDDINGS_KWARGS
)

from src.context import get_config_context
from src.utils.cli_helper import SpecialHelpOrder
from src.modelling.steps.step_text_clustering import StepTextClustering

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
