import pandas as pd 

df_ref = pd.read_excel(r"C:\Users\alarr\Downloads\pour alexandre.xlsx")
df_ref["KEY"] = df_ref["Title"].apply(lambda x : x.lower().strip())
df_my_search = pd.read_excel(r"C:\Users\alarr\Downloads\pour alexandre.xlsx", "MY SEARCH")
df_my_search = df_my_search.drop_duplicates("Title")

df_my_search["KEY"] = df_my_search["Title"].apply(lambda x : x.lower().strip())

final = df_ref.merge(df_my_search, on="KEY", how="left", suffixes=("", "_my_search"))
final.to_csv(r"C:\Users\alarr\Downloads\merged_left.csv", sep=";", index=False)