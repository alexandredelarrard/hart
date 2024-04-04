import pandas as pd 
import shutil
from tqdm import tqdm

if __name__ == "__main__":
    config, context = get_config_context('./configs', use_cache = False, save=False)

    df = pd.read_sql("ALL_ITEMS_202403", con = context.db_con)
    df = df.loc[df["ID_PICTURE"].notnull()]
    df["from"] = df[["SELLER", "ID_PICTURE"]].apply(lambda x: f"./data/{x['SELLER']}/pictures/{x['ID_PICTURE']}.jpg", axis=1)

    a = df.loc[df["TOTAL_DESCRIPTION"].apply(lambda x : " autographe " in " " + x.lower() + " ")]
    save_path = "./data/pictures_training/autographe"

    for row in tqdm(a[["from"]].to_dict(orient="records")[:150]):
        try:
            shutil.copy(row["from"], save_path)
        except Exception as e:
            self._log.warning(e)      