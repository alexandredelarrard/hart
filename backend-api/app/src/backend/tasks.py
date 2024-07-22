import os
from celery import Celery
from datetime import datetime

from src.constants.variables import TEXT_DB_EN, TEXT_DB_FR, PICTURE_DB
from src.extensions import config, context
from src.constants.models import EmbeddingsResults
from src.schemas.results import CloseResult
from src.utils.dataset_retreival import DatasetRetreiver

celery = Celery("src.backend.tasks", broker=config.celery.url)
celery.config_from_object("celeryconfig")

if os.getenv("FLASK_ENV") == "celery_worker":
    from src.modelling.transformers.EmbeddingCollection import EmbeddingCollection
    from src.modelling.transformers.Embedding import StepEmbedding

    # initialize gpu consumptions steps for celery workers only
    step_collection = EmbeddingCollection(context=context, config=config)

    # embeddings
    step_embedding = StepEmbedding(
        context=context, config=config, type=[PICTURE_DB, TEXT_DB_EN, TEXT_DB_FR]
    )

    data_retreiver = DatasetRetreiver(context=context, config=config)


@celery.task(bind=True, time_limit=300)
def process_request(self, image, text) -> dict[str, EmbeddingsResults]:

    new_index = step_collection.name.id_item.lower()
    lower_id_unique = step_collection.name.id_unique.lower()
    task_id = self.request.id

    if image:
        pict_embedding = step_embedding.get_fast_picture_embedding(image)
        results_image = data_retreiver.get_picture_embedding_dist(
            embedding=pict_embedding, limit=100
        )
        df_id_item_pict = data_retreiver.get_id_item_from_pictures(
            list_id_unique=results_image[lower_id_unique].tolist()
        )
        results_image = results_image.merge(
            df_id_item_pict, on=lower_id_unique, how="left", validate="1:1"
        )
        del results_image[lower_id_unique]
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

    # save result to back
    with context.session_scope() as session:
        result = session.query(CloseResult).filter_by(task_id=task_id).first()
        if result:
            result.answer = final.dict()["answer"]
            result.status = "SUCCESS"
            result.result_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            session.commit()

    return final.dict()
