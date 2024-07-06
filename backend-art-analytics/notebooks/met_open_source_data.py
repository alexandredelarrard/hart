import pandas as pd
import os

os.chdir("../")
from src.context import get_config_context

# git lfs clone https://github.com/metmuseum/openaccess

if __name__ == "__main__":
    df = pd.read_csv("D:/data/met/met/infos/MetObjects.csv")

    training_text = pd.read_csv(
        r"C:\Users\alarr\Downloads\training_predicted.csv", sep=";"
    )
    answers = pd.read_csv(r"C:\Users\alarr\Downloads\anwers.csv", sep=";")

    total = pd.concat([training_text, answers], axis=0)
    total = total.drop_duplicates("ID_ITEM")

    config, context = get_config_context("./configs", use_cache=False, save=False)
    full_data = pd.read_sql(
        'SELECT "SELLER", "ID_ITEM", "ID_PICTURE", "URL_FULL_DETAILS" FROM "ALL_ITEMS_202403"',
        con=context.db_con,
    )

    total = total.merge(full_data, on="ID_ITEM", how="left", validate="1:1")
    total.to_csv(r"D:\data\text_training\training_classes.csv", sep=";")
