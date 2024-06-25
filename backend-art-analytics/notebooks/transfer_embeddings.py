import os 
import csv
from datetime import datetime
import tqdm

os.chdir(r"C:\Users\alarr\Documents\repos\hart\backend-art-analytics")
from src.context import get_config_context
from src.modelling.transformers.ChromaCollection import ChromaCollection

config, context = get_config_context('./configs', use_cache = False, save=False)
chroma = ChromaCollection(context=context,
                        config=config,
                        type="picture",
                        n_top_results=25)

ids = chroma.collection.get(include=[])["ids"]
step = 100
with open(r'D:\db_backup\picture_embeddings_truncated.csv', 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['ID_UNIQUE', 'ID_PICTURE', "pict_path", 'CREATED_AT', 'EMBEDDING'])
    
    for i in tqdm.tqdm(range(1)):
        sub_ids = ids[i*step:min((i+1)*step, len(ids))]
        all_data = chroma.collection.get(ids=sub_ids, include=["embeddings", "metadatas"])
        for id, embdding, metadata in zip(all_data["ids"], all_data["embeddings"], all_data["metadatas"]):
            writer.writerow([metadata["ID_UNIQUE"], metadata["ID_PICTURE"], metadata["pict_path"], datetime.now(), embdding])