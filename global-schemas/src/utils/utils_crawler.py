import pandas as pd
from glob import glob
from datetime import datetime
from pathlib import Path
import os
from tqdm import tqdm
import urllib
import pickle
import logging
import hashlib
import json
import shutil

from omegaconf import DictConfig
from src.constants.variables import DATE_FORMAT


def read_crawled_csvs(path: Path):

    # read all csvs
    files = glob(str(path / Path("*.csv")))
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

    if len(liste_dfs) != 0:
        df = pd.concat(liste_dfs, axis=0, ignore_index=True)
    else:
        df = pd.DataFrame()

    logging.info(f"RECORDINGS : {df.shape[0]}")
    logging.info(f"Missing reads of files : {len(not_read)}")

    return df


def read_crawled_pickles(path: Path):

    # read all csvs
    files = glob(str(path / Path("*.pickle")))
    not_read = []
    liste_dfs = []

    for file in tqdm(files):
        try:
            df_file = read_pickle(file)
            file_time = os.path.getmtime(file)
            file_name = os.path.basename(file)
            if isinstance(df_file, dict):
                df_file["FILE_CREATION_DATE"] = file_time
                df_file["FILE"] = file_name
                liste_dfs.append(df_file)
            elif isinstance(df_file, list):
                if len(df_file) != 0:
                    if isinstance(df_file[0], list):
                        df_file = [x[0] for x in df_file]
                    df_file = [
                        dict(
                            item, **{"FILE_CREATION_DATE": file_time, "FILE": file_name}
                        )
                        for item in df_file
                    ]
                liste_dfs += df_file
        except Exception:
            not_read.append(file)

    df = pd.DataFrame(liste_dfs)
    if df.shape[1] == 1:
        df = pd.DataFrame(df[0].tolist())

    logging.info(f"RECORDINGS : {df.shape[0]}")
    logging.info(f"Missing reads of files : {len(not_read)}")

    return df


def read_pickle(path: Path):
    with open(path, "rb") as f:
        df_file = pickle.load(f, encoding="latin-1")
    return df_file


def read_json(path: str):
    with open(path, "r") as f:
        df_file = json.load(f)
    return df_file


def save_json(dico, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dico, f, ensure_ascii=False)


def save_pickle_file(df, path):
    with open(path, "wb") as f:
        pickle.dump(df, f)


def save_picture_crawled(url_picture, image_path, picture_id):
    message = False
    try:
        if not os.path.isfile(image_path / Path(f"{picture_id}.jpg")):
            if "https" in url_picture:
                urllib.request.urlretrieve(
                    url_picture, image_path / Path(f"{picture_id}.jpg")
                )

            if os.path.isfile(image_path / Path(f"{picture_id}.jpg")):
                return True

    except Exception as e:
        logging.error(f"SAVING PICTURE FAILED : {e}")
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
        message = e
        pass
    return message


def save_queue_to_file(queue, path: Path):
    infos = []
    while queue.qsize() != 0:
        infos.append(queue.get())
    save_infos(infos, path)


def save_infos(df: pd.DataFrame, path: Path):

    _, file_extension = os.path.splitext(path)

    if not os.path.exists(os.path.dirname(path)):
        os.mkdir(os.path.dirname(path))

    if file_extension == ".csv":
        df.to_csv(path, index=False, sep=";")
    elif file_extension == ".txt" or file_extension == ".pickle":
        with open(path, "wb") as f:
            pickle.dump(df, f)
    else:
        logging.error(
            f"Extensions handled for saving files are .TXT / .PICKLE or .CSV only. Found {file_extension}"
        )


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


def get_files_already_done(df, to_replace=(), split=[]):

    if df.shape[0] != 0:
        current_url = df["CURRENT_URL"].drop_duplicates()

        if len(split) != 0:
            current_url = current_url.apply(
                lambda x: x.split(split[0])[split[1]]
            ).drop_duplicates()

        if not to_replace:
            return current_url.apply(lambda x: x.replace(".csv", ""))
        else:
            return current_url.apply(
                lambda x: x.replace(".csv", "").replace(to_replace[0], to_replace[1])
            )
    else:
        return []


def get_files_done_from_path(file_path=None, url_path=None):
    files = glob(str(file_path / Path("*.csv")))
    return [url_path + os.path.basename(x).replace(".csv", "") for x in files]


def keep_files_to_do(to_crawl, already_crawled):
    liste_urls = list(set(to_crawl) - set(already_crawled))
    logging.info(
        f"ALREADY CRAWLED {len(already_crawled)} REMAINING {len(liste_urls)} / {len(to_crawl)}"
    )
    return liste_urls


def check_path_exist(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    else:
        pass


def define_save_paths(config: DictConfig, seller, mode="history"):

    paths = {}

    root_path = os.environ.get("ROOT_PATH", None)
    if not root_path:
        root_path = config.paths.root

    crawl_path = config.paths.crawl

    if mode == "new":
        new_path = config.paths.crawl_path_new
    elif mode == "history":
        new_path = ""
    else:
        raise Exception(
            f"Must declare a valid mode of savepath : new or history. Got {mode}"
        )

    logging.info(f"CRAWLING WITH MODE = {mode}")
    paths["pictures"] = Path(
        f"{root_path}/{crawl_path}/{seller}/{config.paths.crawl_picture_path}"
    )
    paths["details"] = Path(
        f"{root_path}/{crawl_path}/{seller}/{new_path}/{config.paths.crawl_details_path}"
    )
    paths["infos"] = Path(
        f"{root_path}/{crawl_path}/{seller}/{new_path}/{config.paths.crawl_infos_path}"
    )
    paths["auctions"] = Path(
        f"{root_path}/{crawl_path}/{seller}/{new_path}/{config.paths.crawl_auctions_path}"
    )

    for _, path in paths.items():
        check_path_exist(path)

    return paths


def define_global_paths(config: DictConfig):

    global_paths = {}

    root_path = os.environ.get("ROOT_PATH", None)
    if not root_path:
        root_path = config.paths.root

    logging.info(f"Root path selected is {root_path}")

    global_paths["ROOT"] = Path(root_path)
    global_paths["CRAWL"] = global_paths["ROOT"] / Path(config.paths.crawl)
    global_paths["MODEL"] = global_paths["ROOT"] / Path(config.paths.model)
    global_paths["DEFAULT"] = global_paths["ROOT"] / Path(config.paths.default)
    global_paths["ARTIST"] = global_paths["ROOT"] / Path(config.paths.artist)
    global_paths["LLM"] = global_paths["ROOT"] / Path(config.paths.llm)
    global_paths["LLM_TO_EXTRACT"] = (
        global_paths["ROOT"]
        / Path(config.paths.llm)
        / Path(config.paths.features_to_extract)
    )
    global_paths["LLM_EXTRACTED"] = (
        global_paths["ROOT"]
        / Path(config.paths.llm)
        / Path(config.paths.llm_extraction)
    )
    global_paths["TRAINING_PICTURES"] = global_paths["ROOT"] / Path(
        config.paths.picture_training
    )
    global_paths["TRAINING_TEXT"] = global_paths["ROOT"] / Path(
        config.paths.text_training
    )

    for _, path in global_paths.items():
        check_path_exist(path)

    return global_paths


def define_end_date(end_date):
    if end_date:
        return pd.to_datetime(end_date, format=DATE_FORMAT)
    else:
        return pd.to_datetime(datetime.today())


def define_start_date(start_date, history_start_year):
    if start_date:
        return pd.to_datetime(start_date, format=DATE_FORMAT)
    else:
        return pd.to_datetime(history_start_year, format="%Y")
