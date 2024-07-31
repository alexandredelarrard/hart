from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Integer
from src.constants.models import FullResultInfos

Base = declarative_base()


class AllItems(Base):
    __tablename__ = "ALL_ITEMS"
    __table_args__ = {"extend_existing": True}

    id_item = Column(String, nullable=False, primary_key=True)
    id_auction = Column(String, nullable=False)
    ID_PICTURE = Column(String)
    AUCTION_DATE = Column(String)
    LOCALISATION = Column(String)
    LOT_NUMBER = Column(Integer)
    SELLER = Column(String)
    HOUSE = Column(String)
    TYPE_SALE = Column(Integer)
    URL_AUCTION = Column(String)
    URL_FULL_DETAILS = Column(String)
    AUCTION_TITLE = Column(String)
    DETAIL_TITLE = Column(String)
    TOTAL_DESCRIPTION = Column(String)
    CURRENCY = Column(String)
    FINAL_RESULT = Column(Float)
    MIN_ESTIMATION = Column(Float)
    MAX_ESTIMATION = Column(Float)
    EUR_FINAL_RESULT = Column(Float)
    EUR_MIN_ESTIMATION = Column(Float)
    EUR_MAX_ESTIMATION = Column(Float)
    IS_FINAL_RESULT = Column(Integer)

    class Config:
        orm_mode = True

    def to_dict(self):
        return {
            "id_item": self.id_item,
            "id_picture": self.ID_PICTURE,
            "url_full_detail": self.URL_FULL_DETAILS,
            "estimate_min": self.EUR_MIN_ESTIMATION,
            "estimate_max": self.EUR_MAX_ESTIMATION,
            "final_result": self.EUR_FINAL_RESULT,
            "currency": self.CURRENCY,
            "localisation": self.LOCALISATION,
            "date": self.AUCTION_DATE,
            "house": self.HOUSE,
            "seller": self.SELLER,
            "title": self.DETAIL_TITLE,
            "description": self.TOTAL_DESCRIPTION,
        }

    def to_dict_search(self):
        return FullResultInfos(
            id_item=self.id_item,
            id_picture=str(self.ID_PICTURE).strip("[]").strip("{}").split(",")[0],
            pictures=str(self.ID_PICTURE).strip("[]").strip("{}").split(","),
            title=self.DETAIL_TITLE,
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
