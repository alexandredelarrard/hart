import pandas as pd 
import shutil 
import tqdm 
df_ref = pd.read_excel(r"C:\Users\alarr\Downloads\pour alexandre.xlsx")
df_ref["KEY"] = df_ref["Title"].apply(lambda x : x.lower().strip())
df_my_search = pd.read_excel(r"C:\Users\alarr\Downloads\pour alexandre.xlsx", "MY SEARCH")
df_my_search = df_my_search.drop_duplicates("Title")

df_my_search["KEY"] = df_my_search["Title"].apply(lambda x : x.lower().strip())

final = df_ref.merge(df_my_search, on="KEY", how="left", suffixes=("", "_my_search"))
final.to_csv(r"C:\Users\alarr\Downloads\merged_left.csv", sep=";", index=False)

if __name__ == "__main__":
    df = pd.read_csv(r"D:\data\text_training\training_classes.csv", sep=";")

    for row in tqdm.tqdm(df.loc[0.99>df["PROBA_0"]].to_dict(orient="records")):
        try:
            shutil.copy(f"D:/data/{row["SELLER"]}/pictures/{row["ID_PICTURE"]}.jpg",
                    r"E:\art_project\pictures")
        except Exception:
            pass