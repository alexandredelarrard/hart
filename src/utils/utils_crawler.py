import pandas as pd 
from typing import List
from glob import glob
import os 
from tqdm import tqdm
import urllib
import logging

def read_crawled_csvs(path):

    # read all csvs
    files = glob(path + "/*.csv")
    not_read = []
    
    liste_dfs = []
    for file in tqdm(files): 
        try:
            df_file = pd.read_csv(file, sep=";")
            df_file["FILE"] = os.path.basename(file)
            liste_dfs.append(df_file)
        except Exception:
            not_read.append(file)

    df = pd.concat(liste_dfs, 
                    axis=0, 
                    ignore_index=True)

    logging.info(f"RECORDINGS : {df.shape[0]}")
    logging.info(f"Missing reads of files : {len(not_read)}")

    return df

def get_files_already_done(file_path, url_path, to_replace=()):
    files_already_done = glob(file_path + "/*.csv")
    if not to_replace:
        files_already_done = [url_path + os.path.basename(x).replace(".csv","")
                                                for x in files_already_done]
    else:
        files_already_done = [url_path + os.path.basename(x).replace(".csv","")\
                                                .replace(to_replace[0], to_replace[1])
                                                for x in files_already_done]

    return files_already_done

def keep_files_to_do(to_crawl, already_crawled):
    liste_urls = list(set(to_crawl) - set(already_crawled))
    logging.info(f"ALREADY CRAWLED {len(already_crawled)} REMAINING {len(liste_urls)}")
    return liste_urls

def save_picture_crawled(url_picture, image_path, picture_id):

    try:
        if not os.path.isfile(image_path + f"/{picture_id}.jpg"):
            if "https" in url_picture:
                urllib.request.urlretrieve(url_picture, image_path + f"/{picture_id}.jpg")
    except Exception:
        pass