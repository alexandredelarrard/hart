import os
import logging
from celery import Celery

from src.extensions import config, context
from src.constants.models import EmbeddingsResults
from src.utils.dataset_retreival import DatasetRetreiver


celery = Celery("src.backend.tasks", broker=config.celery.url)
celery.config_from_object("celeryconfig")

if os.getenv("FLASK_ENV") == "celery_worker":
    from src.transformers.EmbeddingCollection import EmbeddingCollection
    from src.transformers.Embedding import StepEmbedding

    from src.constants.variables import TEXT_DB_EN, TEXT_DB_FR, PICTURE_DB

    # initialize gpu consumptions steps for celery workers only
    step_collection = EmbeddingCollection(context=context, config=config)

    # embeddings
    step_embedding = StepEmbedding(
        context=context, config=config, type=[PICTURE_DB, TEXT_DB_EN, TEXT_DB_FR]
    )

    data_retreiver = DatasetRetreiver(context=context, config=config)


@celery.task(time_limit=300)
def process_request(image, text) -> dict[str, EmbeddingsResults]:

    new_index = step_collection.name.id_item.lower()

    if image:
        pict_embedding = step_embedding.get_fast_picture_embedding(image)
        results_image = data_retreiver.get_picture_embedding_dist(
            table=PICTURE_DB, embedding=pict_embedding, limit=100
        )
        results_image = results_image.drop_duplicates(new_index)

    if text:
        language_db = step_collection.detect_language(text)
        text_embedding = step_embedding.get_text_embedding(language_db, text)
        results_text = data_retreiver.get_text_embedding_dist(
            table=language_db, embedding=text_embedding, limit=100
        )
        results_text = results_text.drop_duplicates(new_index)

    # TODO: multiembedding model distance (multimodal)
    if text and image:
        final = step_collection.multi_embedding_strat(results_image, results_text)
        final = step_collection.fill_EmbeddingsResults(
            liste_results=final.set_index(new_index).to_dict(orient="index")
        )
    elif text and not image:
        final = step_collection.fill_EmbeddingsResults(
            liste_results=results_text.set_index(new_index).to_dict(orient="index")
        )
    else:
        final = step_collection.fill_EmbeddingsResults(
            liste_results=results_image.set_index(new_index).to_dict(orient="index")
        )
    return final.dict()
