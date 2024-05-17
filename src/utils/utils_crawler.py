import pandas as pd 
from glob import glob
from datetime import datetime
import os 
from tqdm import tqdm
import urllib
import pickle
import logging
import hashlib
import json 
import shutil

from omegaconf import DictConfig
from src.constants.variables import date_format

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

    if len(liste_dfs) !=0:
        df = pd.concat(liste_dfs, axis=0, ignore_index=True)
    else:
        df = pd.DataFrame()
    
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
    if df.shape[1] == 1:
        df = pd.DataFrame(df[0].tolist())

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
    with open(path, "w", encoding='utf-8') as f:
        json.dump(dico, f, ensure_ascii=False)

def save_pickle_file(df, path):
    with open(path, "wb") as f:
        pickle.dump(df, f)

def save_picture_crawled(url_picture, image_path, picture_id):
    message = ""
    try:
        if not os.path.isfile(image_path + f"/{picture_id}.jpg"):
            if "https" in url_picture:
                urllib.request.urlretrieve(url_picture, image_path + f"/{picture_id}.jpg")
    except Exception as e:
        logging.error(f"SAVING PICTURE FAILED : {e}")
        message= e
        pass
    return message


def save_canvas_picture(picture, image_path, picture_id):
    message = ""
    try:
        if picture != "" and not os.path.isfile(image_path + f"/{picture_id}.jpg"):
            with open(image_path + f"/{picture_id}.jpg", "wb") as f:
                f.write(picture)
    except Exception as e:
        logging.error(f"SAVING PICTURE FAILED : {e}")
        message= e
        pass
    return message

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

def move_picture(path_from, path_to):
    if not os.path.exists(path_to):
        os.mkdir(path_to)
    shutil.move(path_from, path_to)

def encode_file_name(x):
    return hashlib.sha256(str.encode(x)).hexdigest()

def get_files_already_done(df, to_replace=(), split = []):

    if df.shape[0] !=0:
        current_url = df["CURRENT_URL"].drop_duplicates()
        
        if len(split) !=0:
            current_url = current_url.apply(lambda x: x.split(split[0])[split[1]]).drop_duplicates()

        if not to_replace:
            return current_url.apply(lambda x: x.replace(".csv",""))
        else:
            return current_url.apply(lambda x: x.replace(".csv","").replace(to_replace[0], to_replace[1]))
    else:
        return []
    
def get_files_done_from_path(file_path=None, url_path=None):
    files = glob(file_path + "/*.csv")
    return [url_path + os.path.basename(x).replace(".csv", "") for x in files]

def keep_files_to_do(to_crawl, already_crawled):
    liste_urls = list(set(to_crawl) - set(already_crawled))
    logging.info(f"ALREADY CRAWLED {len(already_crawled)} REMAINING {len(liste_urls)} / {len(to_crawl)}")
    return liste_urls

def check_path_exist(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def define_save_paths(config : DictConfig, seller, mode="history"):

    paths = {}
    root_path = config.crawling.root_path

    if mode=="new":
        new_path = config.crawling.path_new
    elif mode=="history":
        new_path = ""
    else:
        raise Exception(f"Must declare a valid mode of savepath : new or history. Got {mode}")
    
    logging.info(f"CRAWLING WITH MODE = {mode}")
    paths["pictures"] = f"{root_path}/{seller}/{config.crawling.picture_path}"
    paths["details"] = f"{root_path}/{seller}/{new_path}/{config.crawling.details_path}"
    paths["infos"] = f"{root_path}/{seller}/{new_path}/{config.crawling.infos_path}"
    paths["auctions"] = f"{root_path}/{seller}/{new_path}/{config.crawling.auctions_path}"

    for _, path in paths.items():
        check_path_exist(path)

    return paths

def define_end_date(end_date):
    if end_date:
        return pd.to_datetime(end_date, format=date_format)
    else:
        return pd.to_datetime(datetime.today())

def define_start_date(start_date, history_start_year):
    if start_date:
        return pd.to_datetime(start_date, format=date_format)
    else:
        return pd.to_datetime(history_start_year, format="%Y")