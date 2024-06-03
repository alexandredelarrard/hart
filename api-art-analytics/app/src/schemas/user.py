from src.extensions import db

class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

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
    
    