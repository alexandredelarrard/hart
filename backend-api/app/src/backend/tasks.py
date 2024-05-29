from celery import Celery
from src.backend.embeddings import create_embedding
from src.backend.chroma_db import compare_embeddings
from src.extensions import config

celery = Celery('src.backend.tasks', broker=config.celery.url) #'redis://redis:6379/0'
celery.config_from_object('celeryconfig')

@celery.task
def process_request(image, text):
    embedding = create_embedding(image, text)
    results = compare_embeddings(embedding)
    return results  