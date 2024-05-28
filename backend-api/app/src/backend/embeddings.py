import numpy as np

def create_embedding(image, text):
    # Dummy function to create embeddings from image and text
    image_embedding = np.random.rand(128)
    text_embedding = np.random.rand(128)
    return np.concatenate((image_embedding, text_embedding))