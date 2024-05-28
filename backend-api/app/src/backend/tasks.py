from celery import Celery
from .embeddings import create_embedding
from .chroma_db import compare_embeddings
from src.extensions import config

celery = Celery('tasks', broker=config.celery.url) #'redis://redis:6379/0'

@celery.task
def process_request(image, text):
    embedding = create_embedding(image, text)
    results = compare_embeddings(embedding)
    return results  