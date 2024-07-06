from pgvector.sqlalchemy import Vector
from datetime import datetime
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import Dict
from src.utils.step import Step
import numpy as np
from tqdm import tqdm
from src.constants.variables import (PICTURE_TYPE,
                                    TEXT_TYPE_FR,
                                    TEXT_TYPE_EN,
                                    ID_TEXT,
                                    ID_UNIQUE)

class SchemaEmbeddings(Step):

    def __init__(self, context, config):

        super().__init__(context=context, config=config)
        db = context.flask_db

        class _Picture_Embeddings(db.Model):
            __tablename__ = 'picture_embeddings'
            __table_args__ = {'extend_existing': True}
            id_unique = db.Column(db.String(120), unique=True, primary_key=True)
            id_picture = db.Column(db.String(120), nullable=True)
            pict_path = db.Column(db.String(120), nullable=True)
            created_at = db.Column(db.DateTime, nullable=False)
            embedding = db.Column(Vector(1024))

            def to_dict(self):
                return {c.name: getattr(self, c.name) for c in self.__table__.columns}
            
        class _Text_Embeddings_fr(db.Model):
            __tablename__ = 'text_embeddings_french'
            __table_args__ = {'extend_existing': True}
            id_item = db.Column(db.String(120), unique=True, primary_key=True)
            created_at = db.Column(db.DateTime, nullable=False)
            embedding = db.Column(Vector(1024))

            def to_dict(self):
                return {c.name: getattr(self, c.name) for c in self.__table__.columns}
            
        class _Text_Embeddings_en(db.Model):
            __tablename__ = 'text_embeddings_english'
            __table_args__ = {'extend_existing': True}
            id_item = db.Column(db.String(120), unique=True, primary_key=True)
            created_at = db.Column(db.DateTime, nullable=False)
            embedding = db.Column(Vector(1024))

            def to_dict(self):
                return {c.name: getattr(self, c.name) for c in self.__table__.columns}

        self.collections = {}    
        self.collections[PICTURE_TYPE] = _Picture_Embeddings
        self.collections[TEXT_TYPE_FR] = _Text_Embeddings_fr
        self.collections[TEXT_TYPE_EN] = _Text_Embeddings_en
        

class FillDBEmbeddings(SchemaEmbeddings):

    def __init__(self, context, config, type : str = PICTURE_TYPE):
        super().__init__(context=context, config=config)

        if type in [PICTURE_TYPE, TEXT_TYPE_FR, TEXT_TYPE_EN]:
            self.collection = self.collections[type]
        else:
            raise Exception("Either text_fr, text_en or picture values for type")
        
        self.db = context.flask_db
        self.id_column = ID_UNIQUE.lower() if type == PICTURE_TYPE else ID_TEXT.lower()

    def get_ids(self):
        df= self.read_sql_data(f"SELECT \"{self.id_column}\" FROM \"{self.collection.__tablename__}\"")
        return df[self.id_column].tolist()
    
    def save_collection(self, list_descriptions : Dict, results : np.array):
        self.session = scoped_session(sessionmaker(bind=self._context.db_con))
        for key, values in results.items():
            for observation, description in tqdm(zip(values, list_descriptions)):
                if key in [TEXT_TYPE_FR, TEXT_TYPE_EN]:
                    new_item = self.collection(
                                          id_item=description[self.name.id_item],
                                          created_at=datetime.now(),
                                          embedding=observation.tolist())
                if key == PICTURE_TYPE:
                    new_item = self.collection(
                                        id_unique=description[self.name.id_unique],
                                        id_picture=description[self.name.id_picture],
                                        pict_path=description["pict_path"],
                                        created_at=datetime.now(),
                                        embedding=observation.tolist())
                
                self.session.add(new_item)
            self.session.commit()
        self.session.close()
    
    def delete_duplicates(self):
        self.session = scoped_session(sessionmaker(bind=self._context.db_con))
        
        subquery = (
            self.session.query(
                self.id_column,
                self.db.func.min(self.collection.created_at).label('min_created_at')
            )
            .group_by(self.id_column)
            .subquery()
        )

        duplicates = (
            self.session.query(self.collection)
            .join(
                subquery,
                (getattr(self.collection, self.id_column.name) == getattr(subquery.c, self.id_column.name)) &
                (self.collection.created_at != subquery.c.min_created_at)
            )
            .all()
        )

        for duplicate in duplicates:
            self.session.delete(duplicate)

        self.session.commit()
        self.session.close()