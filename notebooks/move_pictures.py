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

    df = pd.read_sql("SELECT \"SELLER\", \"ID_PICTURE\", \"TOTAL_DESCRIPTION\" FROM \"ALL_ITEMS_202403\" WHERE \"ID_PICTURE\" IS NOT NULL AND LENGTH(\"TOTAL_DESCRIPTION\") > 100", 
                     con = context.db_con)
    df["from"] = df[["SELLER", "ID_PICTURE"]].swifter.apply(lambda x: f"D:/data/{x['SELLER']}/pictures/{x['ID_PICTURE']}.jpg", axis=1)

    a = df.loc[df["TOTAL_DESCRIPTION"].apply(lambda x : " bonbonnière " in " " + x.lower() + " ")]
    save_path = "D:/data/test/bonbonniere"

    for row in tqdm(a[["from"]].to_dict(orient="records")[:100]):
        if not os.path.isdir(save_path):
            os.mkdir(save_path)
        try:
            shutil.copy(row["from"], save_path)
        except Exception as e:
            logging.warning(e)      