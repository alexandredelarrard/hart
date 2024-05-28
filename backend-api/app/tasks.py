from celery import Celery
from .embeddings import create_embedding
from .chroma_db import compare_embeddings

celery = Celery('tasks', broker='redis://redis:6379/0')

@celery.task
def process_request(image, text):
    embedding = create_embedding(image, text)
    results = compare_embeddings(embedding)
    return results  