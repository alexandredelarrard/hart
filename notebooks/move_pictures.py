import pandas as pd 
import shutil
from tqdm import tqdm
import logging 
import swifter
import os 

os.chdir("../")
from src.context import get_config_context

if __name__ == "__main__":
    config, context = get_config_context('./configs', use_cache = False, save=False)

    df = pd.read_sql("ALL_ITEMS_202403", con = context.db_con)
    df = df.loc[df["ID_PICTURE"].notnull()]
    df["from"] = df[["SELLER", "ID_PICTURE"]].swifter.apply(lambda x: f"./data/{x['SELLER']}/pictures/{x['ID_PICTURE']}.jpg", axis=1)

    a = df.loc[df["TOTAL_DESCRIPTION"].apply(lambda x : " lettre autographe " in " " + x.lower() + " ")]
    save_path = "./data/pictures_training/lettre autographe"

    for row in tqdm(a[["from"]].to_dict(orient="records")[:200]):
        try:
            shutil.copy(row["from"], save_path)
        except Exception as e:
            logging.warning(e)      