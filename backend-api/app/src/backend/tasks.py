import os 
from celery import Celery
from src.extensions import config, context

celery = Celery('src.backend.tasks', broker=config.celery.url)
celery.config_from_object('celeryconfig')

if os.getenv('FLASK_ENV') == 'celery_worker':
    from src.transformers.ChromaCollection import ChromaCollection
    from src.transformers.Embedding import StepEmbedding
    from src.transformers.GptChat import GptChat

    # initialize gpu consumptions steps for celery workers only
    step_chromadb = ChromaCollection(context=context, config=config)

    # embeddings 
    step_embedding = StepEmbedding(context=context, config=config, 
                                    type=["text", "picture"])
    
    # chatgpt
    # step_gpt = GptChat(config=config, context=context, 
    #                    methode="open_ai")

@celery.task
def process_request(image, text):
    results = {"image" : None, "text": None}
    if image:
        pict_embedding = step_embedding.get_fast_picture_embedding(image)
        results['image'] = step_chromadb.query_collection(pict_embedding)
    if text:
        text_embedding = step_embedding.get_text_embedding(text, prompt_name=config.embedding.prompt_name)
        results['text'] = step_chromadb.query_collection(text_embedding)
    return results  

@celery.task
def chat_request(art_pieces, question):
    results, query_status = step_gpt.get_answer(art_pieces=art_pieces, question=question)
    print(query_status)
    return results