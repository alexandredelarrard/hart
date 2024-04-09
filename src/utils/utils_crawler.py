import pandas as pd 
from typing import List
from glob import glob
import os 
from tqdm import tqdm
import urllib
import pickle
import logging
import hashlib
import json 
import shutil

def read_crawled_csvs(path : str):

    # read all csvs
    files = glob(path + "/*.csv")
    not_read = []
    liste_dfs = []

    for file in tqdm(files): 
        try:
            df_file = pd.read_csv(file, sep=";")
            if "FILE" not in df_file.columns:
                df_file["FILE"] = os.path.basename(file)

            liste_dfs.append(df_file)
        except Exception:
            not_read.append(file)

    df = pd.concat(liste_dfs, axis=0, ignore_index=True)
    
    logging.info(f"RECORDINGS : {df.shape[0]}")
    logging.info(f"Missing reads of files : {len(not_read)}")

    return df

def read_crawled_pickles(path : str):

    # read all csvs
    files = glob(path + "/*.pickle")
    not_read = []
    
    liste_dfs = []
    for file in tqdm(files): 
        try:
            df_file = read_pickle(file)
            if isinstance(df_file, dict):
                df_file["FILE"] = os.path.basename(file)
                liste_dfs.append(df_file)
            elif isinstance(df_file, list):
                liste_dfs += df_file
        except Exception:
            not_read.append(file)

    df = pd.DataFrame(liste_dfs)

    logging.info(f"RECORDINGS : {df.shape[0]}")
    logging.info(f"Missing reads of files : {len(not_read)}")

    return df

def read_pickle(path : str):
    with open(path, "rb") as f:
        df_file = pickle.load(f)
    return df_file

def read_json(path : str):
    with open(path, "r") as f:
        df_file = json.load(f)
    return df_file

def save_json(dico, path: str):
    with open(path, "w") as f:
        json.dump(dico, f)

def save_pickle_file(df, path):
    with open(path, "wb") as f:
        pickle.dump(df, f)

def save_picture_crawled(url_picture, image_path, picture_id):

    try:
        if not os.path.isfile(image_path + f"/{picture_id}.jpg"):
            if "https" in url_picture:
                urllib.request.urlretrieve(url_picture, image_path + f"/{picture_id}.jpg")
    except Exception as e:
        logging.error(f"SAVING PICTURE FAILED : {e}")
        pass

def save_queue_to_file(queue, path):
        infos = []
        while queue.qsize() !=0:
            infos.append(queue.get())
        save_infos(infos, path)
    
def save_infos(df, path):

    if ".csv" in path:
        df.to_csv(path, index=False, sep=";")
    elif ".txt" in path or ".pickle" in path:
        with open(path, "wb") as f:
            pickle.dump(df, f)
    else:
        logging.error("Extensions handled for saving files are .TXT / .PICKLE or .CSV only. Please try again")

def copy_picture(path_from, path_to):
    if not os.path.exists(path_to):
        os.mkdir(path_to)
    shutil.copy(path_from, path_to)

def encode_file_name(file):
    return hashlib.sha256(str.encode(file)).hexdigest()


def get_files_already_done(df, url_path, to_replace=()):
    if not to_replace:
        return df["FILE"].apply(lambda x: url_path + x.replace(".csv",""))
    else:
        return df["FILE"].apply(lambda x: url_path + x.replace(".csv","").replace(to_replace[0], to_replace[1]))

def keep_files_to_do(to_crawl, already_crawled):
    liste_urls = list(set(to_crawl) - set(already_crawled))
    logging.info(f"ALREADY CRAWLED {len(already_crawled)} REMAINING {len(liste_urls)} / {len(to_crawl)}")
    return liste_urls
