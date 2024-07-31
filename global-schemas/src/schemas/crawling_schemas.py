from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from src.constants.variables import DATE_HOUR_FORMAT


class Auctions(BaseModel):
    __tablename__ = "_raw_crawling_auctions"
    __table_args__ = {"extend_existing": True}

    id_auction: str = Field(description="unique auction ID")
    URL_AUCTION: str = Field(description="url of the auction for a seller")
    AUCTION_TITLE: str = Field(description="title of the auction")
    AUCTION_DATE: str = Field(description="date when the auction is done")
    TYPE_SALE: str | None = Field(None, description="Type of sale, online, presence ?")
    SELLER: str = Field(description="website crawled, close to house except for drouot")
    LOCALISATION: str | None = Field(None, description="Where the auction took place")
    HOUSE: str = Field(description="House of auction (for Drouot)")
    FILE: Optional[str] | None = Field(
        None, description="file where info was first saved"
    )
    URL_CRAWLED: str = Field(description="url crawled")
    DATE_CREATION: str = Field(
        datetime.now().strftime(DATE_HOUR_FORMAT), description="When it was crawled"
    )


class Items(BaseModel):
    __tablename__ = "_raw_crawling_items"
    __table_args__ = {"extend_existing": True}

    id_item: str = Field(description="unique auction ID")
    id_auction: str = Field(description="unique auction ID")
    URL_AUCTION: str = Field(description="url of the auction for a seller")
    URL_FULL_DETAILS: str = Field(description="url of the item details")
    AUCTION_DATE: str = Field(None, description="date when the auction is done")
    LOT_NUMBER: str = Field(None, description="lot in the auction")
    ITEM_TITLE: str = Field(None, description=" title of the item")
    ITEM_DESCRIPTION: str | None = Field(None, description="infos from the item")
    ESTIMATE: str | None = Field(None, description="price from the item")
    RESULT: str | None = Field(None, description="result from the item")
    FILE: Optional[str] | None = Field(None, description="file name saved")
    SELLER: str = Field(description="website crawled, close to house except for drouot")
    DATE_CREATION: str = Field(
        datetime.now().strftime(DATE_HOUR_FORMAT), description="When it was crawled"
    )


class Details(BaseModel):
    __tablename__ = "_raw_crawling_details"
    __table_args__ = {"extend_existing": True}

    id_item: str = Field(description="unique item ID")
    URL_FULL_DETAILS: str = Field(description="url of the item details")
    DETAIL_TITLE: str | None = Field(None, description=" title of the item")
    DETAIL_DESCRIPTION: str = Field(description="infos from the item")
    ESTIMATE: str | None = Field(None, description="price from the item")
    RESULT: str | None = Field(None, description="result from the item")
    URL_PICTURE: List[str] | None = Field(None, description="url off the picture")
    ID_PICTURE: List[str] | None = Field(
        None, description="unique ID of the PICTURE based on its url"
    )
    SELLER: str = Field(description="website crawled, close to house except for drouot")
    DATE_CREATION: str = Field(
        datetime.now().strftime(DATE_HOUR_FORMAT), description="When it was crawled"
    )


class Pictures(BaseModel):
    __tablename__ = "_raw_pictures"
    __table_args__ = {"extend_existing": True}

    id_picture: str = Field(description="unique picture ID")
    list_id_item: List[str] = Field(description="unique item ID")
    URL_PICTURE: str = Field(description="url off the picture")
    IS_FILE: bool = Field(description="If the picture is downloaded and saved")
    SELLER: str = Field(description="seller from which the picture was downloaded")
    DATE_CREATION: str = Field(
        datetime.now().strftime(DATE_HOUR_FORMAT), description="When it was crawled"
    )
