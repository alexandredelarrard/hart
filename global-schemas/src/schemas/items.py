from src.extensions import db
from src.constants.models import FullResultInfos


class AllItems(db.Model):
    __table__ = db.Model.metadata.tables["ALL_ITEMS"]
    __table_args__ = {"extend_existing": True}

    def to_dict(self):
        return {
            "id_unique": self.ID_UNIQUE,
            "id_picture": self.ID_PICTURE,
            "id_item": self.ID_ITEM,
            "url_full_detail": self.URL_FULL_DETAILS,
            "estimate_min": self.EUR_MIN_ESTIMATION,
            "estimate_max": self.EUR_MAX_ESTIMATION,
            "final_result": self.EUR_FINAL_RESULT,
            "currency": self.CURRENCY,
            "localisation": self.LOCALISATION,
            "date": self.AUCTION_DATE,
            "house": self.HOUSE,
            "seller": self.SELLER,
            "title": self.ITEM_TITLE_DETAIL,
            "description": self.TOTAL_DESCRIPTION,
        }


class AllPerItem(db.Model):
    __table__ = db.Model.metadata.tables["ALL_ITEMS_per_item"]
    __table_args__ = {"extend_existing": True}

    def to_dict_search(self):
        return FullResultInfos(
            id_item=self.ID_ITEM,
            id_picture=str(self.ID_PICTURE)
            .replace("{", "")
            .replace("}", "")
            .split(",")[0],
            pictures=str(self.ID_PICTURE).replace("{", "").replace("}", "").split(","),
            title=self.ITEM_TITLE_DETAIL,
            description=self.TOTAL_DESCRIPTION,
            estimate_min=self.EUR_MIN_ESTIMATION,
            estimate_max=self.EUR_MAX_ESTIMATION,
            localisation=self.LOCALISATION,
            final_result=self.EUR_FINAL_RESULT,
            date=self.AUCTION_DATE,
            seller=self.SELLER,
            house=self.HOUSE,
            url_full_detail=self.URL_FULL_DETAILS,
        )
