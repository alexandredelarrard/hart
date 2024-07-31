from typing import List
from omegaconf import DictConfig

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.modelling.transformers.Embedding import StepEmbedding
from src.utils.dataset_retreival import DatasetRetreiver
from src.schemas.embedding_schemas import FillDBEmbeddings
from src.constants.variables import (
    TEXT_DB_EN,
    TEXT_DB_FR,
    PICTURE_DB,
)


class StepFillDBEmbeddings(Step):

    def __init__(self, context: Context, config: DictConfig, type: str = PICTURE_DB):

        super().__init__(context=context, config=config)
        self.limite = 500
        self.type = type

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

        # create text embedding
        results = self.get_embeddings(df_desc["target"].tolist())

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
            return self.data_retreiver.get_all_pictures(limit=self.limite)
        elif self.type in [TEXT_DB_FR, TEXT_DB_EN]:
            return self.data_retreiver.get_all_text(
                limit=self.limite, embedding_table_name=self.type
            )
        else:
            raise Exception("either text or picture for get data in vector db fill")
