
# for crawling & cleaning steps : naming
class Naming:
    def __init__(self):
        self.seller = "SELLER"
        self.auction_infos = "AUCTION_INFOS"
        self.item_infos = "ITEM_INFOS"

        self.item_description = "ITEM_DESCRIPTION"
        self.detailed_description = "DETAIL_DESCRIPTION"
        self.total_description = "TOTAL_DESCRIPTION"

        self.auction_title = "AUCTION_TITLE"
        self.item_title = "ITEM_TITLE"
        self.detailed_title = "ITEM_TITLE_DETAIL"

        self.lot = 'LOT_NUMBER'
        self.type_sale = "TYPE_SALE"
        self.house = "HOUSE"
        self.place = "PLACE"

        self.url_detail = "URL_DETAIL"
        self.url_full_detail = "URL_FULL_DETAILS"
        self.url_auction = "URL_AUCTION"
        self.url_item = "URL_ITEM"
        self.url_picture = "URL_PICTURE"
        self.pictures_list_url = "PICTURES_URL"

        self.min_estimate = "MIN_ESTIMATION"
        self.eur_min_estimate = "EUR_MIN_ESTIMATION"
        self.max_estimate = "MAX_ESTIMATION"
        self.eur_max_estimate = "EUR_MAX_ESTIMATION"
        self.brut_estimate = "BRUT_ESTIMATE"
        self.brut_result = "BRUT_RESULT"
        self.item_result = "FINAL_RESULT"
        self.eur_item_result = "EUR_FINAL_RESULT"
        self.is_item_result = "IS_FINAL_RESULT"
        self.auctionner_estimate = "EXPERT_ESTIMATION"

        self.localisation = "LOCALISATION"
        self.country = "COUNTRY"
        self.currency = "CURRENCY"
        self.currency_coef_eur = "CURRENCY_CEOF"
        
        self.date = "AUCTION_DATE"
        self.hour = "AUCTION_HOUR"
        self.sold_year = "AUCTION_YEAR"

        self.auction_file = "AUCTION_FILE"
        self.item_file = "ITEM_FILE"
        self.detail_file = "DETAIL_FILE"

        self.id_picture = "ID_PICTURE"
        self.id_item = "ID_ITEM"
        self.id_auction = "AUCTION_ID"

        self.category = "CATEGORY"
        self.prompt_description = "PROMPT"

        # clustering variable
        self.cluster_id = "label"
        self.cluster_top_words = "labels_top_words"

        self.root_dict = {"LOT" : self.lot,
                        "RESULT" : self.brut_result,
                        "RESULTAT" : self.brut_result,
                        "ESTIMATE" : self.brut_estimate,
                        "ESTIMATION" : self.brut_estimate,
                        "PICTURE_ID" : self.id_picture,
                        "NOM_VENTE" : self.auction_title,
                        "TYPE" : self.type_sale,
                        "NUMBER_LOT" : self.lot,
                        "ID" : self.id_item,
                        "DATE" : self.date,
                        "HOUR" : self.hour}
    
    def dict_rename_auctions(self):
        return {**self.root_dict, **{"TITLE" : self.auction_title,
                                    "INFOS" : self.auction_infos,
                                    "FILE" : self.auction_file}}

    def dict_rename_items(self):
        return {**self.root_dict, **{"TITLE" : self.item_title,
                                    "SALE" : self.brut_estimate,
                                    "CURRENT_URL": self.url_auction,
                                    "INFOS" :self.item_infos,
                                    "FILE" : self.item_file, 
                                    "URL_FULL_DETAIL": self.url_full_detail,
                                    "DESCRIPTION": self.item_description}}
    
    def dict_rename_detail(self):
        return {**self.root_dict, **{"URL" : self.url_full_detail,
                                    "CURRENT_URL": self.url_full_detail,
                                    "URL_DETAIL" : self.url_full_detail,
                                    "URL_FULL_DETAIL": self.url_full_detail,
                                    "DETAIL" : self.detailed_description,
                                    "TITLE" : self.item_title,
                                    "DESCRIPTION": self.detailed_description,
                                    "FILE" : self.detail_file}}

class Artists:
    def __init__(self):
        self.artist_family_name = "ARTIST_FAMILY_NAME"
        self.artist_surname = "ARTIST_SURNAME"
        self.artist_year_born = "ARTIST_YEAR_BORN"
        self.artist_year_death = "ARTIST_YEAR_DEATH"

# date format 
date_format = "%Y-%m-%d"

#for data cleaning
currencies = 'USD|CAD|GBP|CHF|EUR|MAD|JPY|AED|MXN|CZK|PLN|CNY|HKD|NLG|AUD|ESP|SGD|DEM|ITL|INR|FRF|TWD|RMB'
localisation = "London|New York|Hong Kong|Paris|Geneva|Milan|Amsterdam|Zurich|Toronto|Dubai|Doha|Beijing|Mumbai|Derbyshire|Miami|Palm Beach|Chatsworth|Tel Aviv|Singapore|San Francisco|Monaco"

fixed_eur_rate = {"NLG" : 1/2.20371,
                 "FRF" : 1/6.55957,
                 "ITL" : 1/1936.27,
                 "ESP" : 1/200,
                 "DEM" : 0.511292,
                 "MAD" : 0.091} # former currencies before euro

liste_currency_paires = ["USDEUR", "GBPEUR", "CHFEUR", "SEKEUR", "INREUR",
                        "PLNEUR", "CADEUR", "AEDEUR", "HKDEUR", "SGDEUR",
                        "MADEUR", "AUDEUR", "CNYEUR", "JPYEUR", "TWDEUR"]

# for steps 
list_sellers = ["sothebys", "drouot", "christies"]

## TEXT DATABASE NAME
CHROMA_TEXT_DB_NAME="text"
CHROMA_PICTURE_DB_NAME="pictures"