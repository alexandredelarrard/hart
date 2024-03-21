import pandas as pd 
from typing import List
from glob import glob
import os 
from tqdm import tqdm
import urllib
import pickle
import logging
import hashlib

def read_crawled_csvs(path : str):

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
            with open(file, "rb") as f:
                df_file = pickle.load(f)
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


def encode_file_name(file):
    return hashlib.sha256(str.encode(file)).hexdigest()


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
    logging.info(f"ALREADY CRAWLED {len(already_crawled)} REMAINING {len(liste_urls)} / {len(to_crawl)}")
    return liste_urls

def save_picture_crawled(url_picture, image_path, picture_id):

    try:
        if not os.path.isfile(image_path + f"/{picture_id}.jpg"):
            if "https" in url_picture:
                urllib.request.urlretrieve(url_picture, image_path + f"/{picture_id}.jpg")
    except Exception as e:
        logging.error(f"SAVING PICTURE FAILED : {e}")
        pass