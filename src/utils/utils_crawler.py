import pandas as pd 
from glob import glob
import os 
from tqdm import tqdm

import logging


def read_crawled_csvs(path):

    # read all csvs
    files = glob(path + "/*.csv")
    
    liste_dfs = []
    for file in tqdm(files): 
        df_file = pd.read_csv(file, sep=";")
        df_file["FILE"] = os.path.basename(file)
        liste_dfs.append(df_file)

    df = pd.concat(liste_dfs, 
                    axis=0, 
                    ignore_index=True)

    logging.info(f"RECORDINGS : {df.shape[0]}")

    return df

def get_files_already_done(file_path, url_path):
        files_already_done = glob(file_path + "/*.csv")
        files_already_done = [url_path + os.path.basename(x).replace(".csv","")
                                                for x in files_already_done]
        return files_already_done

def keep_files_to_do(to_crawl, already_crawled):
    liste_urls = list(set(to_crawl) - set(already_crawled))
    logging.info(f"ALREADY CRAWLED {len(already_crawled)} REMAINING {len(liste_urls)}")
    return liste_urls