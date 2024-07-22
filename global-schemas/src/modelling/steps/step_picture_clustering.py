import os
from tqdm import tqdm
from typing import List
import pandas as pd

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.Clustering import TopicClustering
from src.utils.utils_crawler import copy_picture

from omegaconf import DictConfig


class StepPictureClustering(Step):

    def __init__(self, context: Context, config: DictConfig):

        super().__init__(context=context, config=config)

        self.save_pictures = True
        self.reduce_dimension = False
        self.vector = "PICTURES"
        self.step = 35000

        self.params = self._config.embedding.clustering.params
        self.n_words_cluster = self.params.n_words_cluster

        self.step_cluster = TopicClustering(params=self.params)

    @timing
    def run(self):

        df = self.read_sql_data(
            'SELECT "ID_UNIQUE", "TOP_0", "PROBA_0" FROM "PICTURES_CATEGORY_07_06_2024_286" WHERE "TOP_0"=\'gravure\''
        )
        self._log.info(f"NUMBER OF ELEMENT = {df.shape[0]}")

        # exrtract data from dbeaver
        collection_infos = self.chroma_collection.collection.get(
            ids=df["ID_UNIQUE"].tolist(), include=["embeddings", "metadatas"]
        )
        df_desc = pd.DataFrame(collection_infos["ids"], columns=[self.name.id_unique])
        self.embeddings = collection_infos["embeddings"]
        df_desc[self.name.cluster_id] = 0
        df_desc["batch"] = 0
        df_desc["pict_path"] = [x["pict_path"] for x in collection_infos["metadatas"]]

        for i in range(df.shape[0] // self.step + 1):
            # cluster it all
            df_desc.iloc[i * self.step : min((i + 1) * self.step, df.shape[0]), 1] = (
                self.step_cluster.hdbscan_clustering(
                    self.embeddings[
                        i * self.step : min((i + 1) * self.step, df.shape[0])
                    ]
                )
            )
            df_desc.iloc[i * self.step : min((i + 1) * self.step, df.shape[0]), 2] = i

        df_desc = df_desc.loc[df_desc["label"] != -1]
        df_desc[self.name.cluster_id] = (
            df_desc[self.name.cluster_id].astype(str)
            + "_"
            + df_desc["batch"].astype(str)
        )

        if self.save_pictures:
            self.save_clustered_pictures(df_desc)

    @timing
    def check_is_file(self, df_desc):
        if self.vector not in df_desc.columns:
            df_desc[self.vector] = df_desc[["SELLER", "ID_PICTURE"]].apply(
                lambda x: f"D:/data/{x['SELLER']}/pictures/{x['ID_PICTURE']}.jpg",
                axis=1,
            )

        exists_pict = df_desc[self.vector].swifter.apply(lambda x: os.path.isfile(x))
        df_desc = df_desc[exists_pict].reset_index(drop=True)
        return df_desc

    @timing
    def save_clustered_pictures(self, sub_df):
        sub_df = sub_df.loc[sub_df[self.name.cluster_id] != -1]
        sub_df["TO"] = sub_df[self.name.cluster_id].apply(
            lambda x: f"D:/data/other/{str(x)}"
        )
        for row in tqdm(sub_df.to_dict(orient="records")):
            copy_picture(row["pict_path"], row["TO"])
