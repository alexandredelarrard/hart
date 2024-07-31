from pgvector.sqlalchemy import Vector
from datetime import datetime
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import Dict, List
import numpy as np

from src.utils.step import Step
from src.constants.variables import TEXT_DB_EN, TEXT_DB_FR, PICTURE_DB


class SchemaEmbeddings(Step):

    def __init__(self, context, config):

        super().__init__(context=context, config=config)
        db = context.flask_db

        class _Picture_Embeddings(db.Model):
            __tablename__ = self._config.table_names.picture_embeddings
            __table_args__ = {"extend_existing": True}
            id_picture = db.Column(db.String(120), unique=True, primary_key=True)
            date_creation = db.Column(db.DateTime, nullable=False)
            embedding = db.Column(Vector(1024))

            def to_dict(self):
                return {c.name: getattr(self, c.name) for c in self.__table__.columns}

        class _Text_Embeddings_fr(db.Model):
            __tablename__ = self._config.table_names.text_embeddings_french
            __table_args__ = {"extend_existing": True}
            id_item = db.Column(db.String(120), unique=True, primary_key=True)
            date_creation = db.Column(db.DateTime, nullable=False)
            embedding = db.Column(Vector(1024))

            def to_dict(self):
                return {c.name: getattr(self, c.name) for c in self.__table__.columns}

        class _Text_Embeddings_en(db.Model):
            __tablename__ = self._config.table_names.text_embeddings_english
            __table_args__ = {"extend_existing": True}
            id_item = db.Column(db.String(120), unique=True, primary_key=True)
            date_creation = db.Column(db.DateTime, nullable=False)
            embedding = db.Column(Vector(1024))

            def to_dict(self):
                return {c.name: getattr(self, c.name) for c in self.__table__.columns}

        self.collections = {}
        self.collections[PICTURE_DB] = _Picture_Embeddings
        self.collections[TEXT_DB_FR] = _Text_Embeddings_fr
        self.collections[TEXT_DB_EN] = _Text_Embeddings_en


class FillDBEmbeddings(SchemaEmbeddings):

    def __init__(self, context, config, type: str = PICTURE_DB):

        super().__init__(context=context, config=config)
        self.type = type
        if type in [PICTURE_DB, TEXT_DB_FR, TEXT_DB_EN]:
            self.collection = self.collections[type]
        else:
            raise Exception(
                f"Should be in {[PICTURE_DB, TEXT_DB_FR, TEXT_DB_EN]} values for type"
            )

        self.db = context.flask_db

    def save_collection(self, list_descriptions: List[Dict], results: np.array):
        self.session = scoped_session(sessionmaker(bind=self._context.db_con))
        for i, description in enumerate(list_descriptions):
            if self.type in [TEXT_DB_FR, TEXT_DB_EN]:
                new_item = self.collection(
                    id_item=description[self.name.low_id_item],
                    date_creation=datetime.now(),
                    embedding=list(results[i]),
                )
            if self.type == PICTURE_DB:
                new_item = self.collection(
                    id_picture=description[self.name.low_id_picture],
                    date_creation=datetime.now(),
                    embedding=list(results[i]),
                )
            self.session.add(new_item)
            self.session.commit()
        self.session.close()
