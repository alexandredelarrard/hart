from typing import List

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.Embedding import StepEmbedding
from src.utils.dataset_retreival import DatasetRetreiver
from src.schemas.postgres_schemas import FillDBEmbeddings
from src.constants.variables import (
    TEXT_DB_EN,
    TEXT_DB_FR,
    PICTURE_DB,
    ID_TEXT,
    ID_UNIQUE,
)

from omegaconf import DictConfig


class StepFillDBEmbeddings(Step):

    def __init__(self, context: Context, config: DictConfig, type: str = PICTURE_DB):

        super().__init__(context=context, config=config)

        if type == PICTURE_DB:
            self.full_data = self._config.table_names.full_data_auction_houses
        elif type in [TEXT_DB_EN, TEXT_DB_FR]:
            self.full_data = self._config.table_names.full_data_per_item
        else:
            raise Exception(
                f"Either {TEXT_DB_EN}, {TEXT_DB_FR} or {PICTURE_DB} values for type"
            )

        self.id = ID_UNIQUE.lower() if type == PICTURE_DB else ID_TEXT.lower()
        self.type = type
        self.root = self._config.paths.root
        self.step_embedding = StepEmbedding(
            context=context, config=config, type=[self.type]
        )
        self.data_retreiver = DatasetRetreiver(context=context, config=config)
        self.postgres = FillDBEmbeddings(
            context=self._context, config=config, type=self.type
        )

    @timing
    def run(self):

        # exrtract data from dbeaver, ensure not done and sample to test # 11+ M picts
        df_desc = self.get_data()

        # filter out the ids already embedded
        df_desc = self.filter_out_embeddings_done(df_desc)

        # create text embedding
        results = self.get_embeddings(df_desc[self.vector].tolist())

        # save to chroma db
        self.postgres.save_collection(df_desc.to_dict(orient="records"), results)

    @timing
    def get_embeddings(self, input_list: List[str]):
        if self.type == PICTURE_DB:
            return self.step_embedding.get_batched_picture_embeddings(input_list)
        elif self.type in [TEXT_DB_EN, TEXT_DB_FR]:
            return self.step_embedding.get_batched_text_embeddings(
                language_db=self.type, query_text=input_list
            )
        else:
            raise Exception(
                f"Either {TEXT_DB_EN}, {TEXT_DB_FR} or {PICTURE_DB} values for type"
            )

    @timing
    def get_data(self):
        if self.type == PICTURE_DB:
            self.vector = "pict_path"
            df_desc = self.data_retreiver.get_all_pictures(
                data_name=self.full_data, vector=self.vector, limit=4200000
            )
            return df_desc.drop_duplicates(self.name.id_picture)

        elif self.type in [TEXT_DB_FR, TEXT_DB_EN]:
            langue = "FRENCH" if self.type.split("_")[-1] == "fr" else "ENGLISH"
            df_desc = self.data_retreiver.get_all_text(
                data_name=self.full_data, language=langue, limit=4200000
            )

            # create output var
            self.vector = self.name.total_description
            df_desc[self.vector] = (
                df_desc[langue + "_TITLE"] + " " + df_desc[langue + "_DESCRIPTION"]
            )
            df_desc = df_desc.loc[df_desc[self.vector].str.len() > 20]
            return df_desc.drop_duplicates(self.name.id_item)

        raise Exception("either text or picture for get data in chroma fill")

    @timing
    def filter_out_embeddings_done(self, df_desc):
        done_ids = self.postgres.get_ids()
        df_desc = df_desc.loc[~df_desc[self.id.upper()].isin(done_ids)]
        self._log.info(
            f"DONE IDS in Postgres DB = {len(done_ids)}, TODO = {df_desc.shape[0]}"
        )
        return df_desc
