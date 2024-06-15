from src.extensions import db
import base64

class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)
    surname = db.Column(db.String(120), nullable=False)
    job = db.Column(db.String(120), nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    creation_date = db.Column(db.String(120), nullable=False)
    active = db.Column(db.Boolean, default=False)

    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class AllItems(db.Model):
    __table__ = db.Model.metadata.tables['ALL_ITEMS']

    def to_dict(self):
        return {
            'id_unique': self.ID_UNIQUE,
            'id_picture': self.ID_PICTURE,
            'id_item': self.ID_ITEM,
            'url_full_detail': self.URL_FULL_DETAILS,
            'estimate_min': self.EUR_MIN_ESTIMATION,
            'estimate_max': self.EUR_MAX_ESTIMATION,
            "final_result": self.EUR_FINAL_RESULT,
            "currency": self.CURRENCY,
            "localisation": self.LOCALISATION,
            "date": self.AUCTION_DATE,
            "house": self.HOUSE,
            "seller": self.SELLER,
            "title": self.ITEM_TITLE_DETAIL,
            "description": self.TOTAL_DESCRIPTION
        }
    

class AllPerItem(db.Model):
    __table__ = db.Model.metadata.tables['ALL_ITEMS_per_item']

    def to_dict(self):
        return {
            'id_item': self.ID_ITEM,
            'id_picture': self.ID_PICTURE,
        }
    
class CloseResult(db.Model):
    __tablename__ = 'closeresult'
    __table_args__ = {'extend_existing': True}
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.String(120), nullable=False)
    text = db.Column(db.String(10000), nullable=False)
    file = db.Column(db.String(10000), nullable=False)
    creation_date = db.Column(db.String(120), nullable=False)
    closest_ids = db.Column(db.String(99000), nullable=False)
    closest_distances= db.Column(db.String(1000), nullable=False)
    status = db.Column(db.String(120), nullable=False)
    result_date = db.Column(db.String(120), nullable=False)
    visible_item = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'result_id': self.result_id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'status': self.status,
            'closest_distances': self.closest_distances,
            'closest_ids': self.closest_ids,
            'file': base64.b64encode(self.file.encode(encoding="utf-8")).decode('utf-8'),
            'text': self.text,
            "result_date": self.result_date,
            "visible_item": self.visible_item,
        }
