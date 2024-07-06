import os
from celery import Celery
import pandas as pd

from src.constants.models import EmbeddingsResults, MultiEmbeddingsResults
from src.extensions import config, context

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


@celery.task(time_limit=300)
def process_request(image, text) -> dict[str, EmbeddingsResults]:
    results = MultiEmbeddingsResults()

    if image:
        picture_db = step_collection.get_db_pict_name()
        query = step_collection.get_query(picture_db)
        pict_embedding = step_embedding.get_fast_picture_embedding(image)
        results.image = step_collection.query_collection_postgres(
            query, pict_embedding, picture_db
        )
        results.image.ids = step_collection.get_id_item_from_pict(results["image"].ids)
    if text:
        language_db = step_collection.detect_language(text)
        query = step_collection.get_query(language_db)
        text_embedding = step_embedding.get_text_embedding(language_db, text)
        results.text = step_collection.query_collection_postgres(
            query, text_embedding, language_db
        )

    if text and image:  # TODO: multiembedding model distance (multimodal)
        results.image = step_collection.multi_embedding_strat(results)

    return results
