from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.Embedding import StepEmbedding
from src.utils.dataset_retreival import DatasetRetreiver
from src.schemas.postgres_schemas import FillDBEmbeddings
from src.constants.variables import (
    PICTURE_TYPE,
    TEXT_TYPE_FR,
    TEXT_TYPE_EN,
    ID_TEXT,
    ID_UNIQUE,
)

from omegaconf import DictConfig


class StepFillDBEmbeddings(Step):

    def __init__(self, context: Context, config: DictConfig, type: str = "picture"):

        super().__init__(context=context, config=config)

        if type == PICTURE_TYPE:
            self.full_data = self._config.cleaning.full_data_auction_houses
        elif type in [TEXT_TYPE_FR, TEXT_TYPE_EN]:
            self.full_data = self._config.cleaning.full_data_per_item
        else:
            raise Exception("Either text_fr, text_en or picture values for type")

        self.id = ID_UNIQUE.lower() if type == PICTURE_TYPE else ID_TEXT.lower()
        self.type = type
        self.root = self._config.crawling.root_path
        self.step_embedding = StepEmbedding(
            context=context, config=config, type=self.type
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
        results = self.step_embedding.get_embeddings(df_desc[self.vector].tolist())

        # save to chroma db
        self.postgres.save_collection(df_desc.to_dict(orient="records"), results)

    def get_data(self):
        if self.type == PICTURE_TYPE:
            self.vector = "pict_path"
            df_desc = self.data_retreiver.get_all_pictures(
                data_name=self.full_data, vector=self.vector, limit=4500000
            )
            return df_desc.drop_duplicates(self.name.id_picture)

        elif self.type in [TEXT_TYPE_FR, TEXT_TYPE_EN]:
            langue = "FRENCH" if self.type.split("_")[-1] == "fr" else "ENGLISH"
            df_desc = self.data_retreiver.get_all_text(
                data_name=self.full_data, language=langue, limit=3100000
            )

            # create output var
            self.vector = self.name.total_description
            df_desc[self.vector] = (
                df_desc[langue + "_TITLE"] + " " + df_desc[langue + "_DESCRIPTION"]
            )
            df_desc = df_desc.loc[df_desc[self.vector].str.len() > 20]
            return df_desc.drop_duplicates(self.name.id_item)

        raise Exception("either text or picture for get data in chroma fill")

    def filter_out_embeddings_done(self, df_desc):
        done_ids = self.postgres.get_ids()
        df_desc = df_desc.loc[~df_desc[self.id.upper()].isin(done_ids)]
        self._log.info(
            f"DONE IDS in Postgres DB = {len(done_ids)}, TODO = {df_desc.shape[0]}"
        )
        return df_desc
