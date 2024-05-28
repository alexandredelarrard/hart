def compare_embeddings(embedding):
    # Dummy function to compare embeddings
    # Assume we have a function `get_top_50_similar_embeddings` that interacts with Chroma DB
    results = get_top_50_similar_embeddings(embedding)
    return results

def get_top_50_similar_embeddings(embedding):
    # Dummy data for similar embeddings
    return [{"id": i, "similarity": 0.99 - i*0.01} for i in range(50)]