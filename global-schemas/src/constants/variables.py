# for crawling & cleaning steps : naming
class Naming:
    def __init__(self):

        self.low_id_item = "id_item"
        self.low_id_auction = "id_auction"
        self.low_id_picture = "id_picture"

        self.seller = "SELLER"
        self.auction_infos = "AUCTION_INFOS"
        self.item_infos = "ITEM_INFOS"

        self.item_description = "ITEM_DESCRIPTION"
        self.detailed_description = "DETAIL_DESCRIPTION"
        self.detailed_title = "DETAIL_TITLE"
        self.total_description = "TOTAL_DESCRIPTION"

        self.auction_title = "AUCTION_TITLE"
        self.item_title = "ITEM_TITLE"

        self.lot = "LOT_NUMBER"
        self.type_sale = "TYPE_SALE"
        self.house = "HOUSE"
        self.place = "PLACE"

        self.url_crawled = "URL_CRAWLED"
        self.url_detail = "URL_DETAIL"
        self.url_full_detail = "URL_FULL_DETAILS"
        self.url_auction = "URL_AUCTION"
        self.url_item = "URL_ITEM"
        self.url_picture = "URL_PICTURE"
        self.is_file = "IS_FILE"

        self.min_estimate = "MIN_ESTIMATION"
        self.eur_min_estimate = "EUR_MIN_ESTIMATION"
        self.max_estimate = "MAX_ESTIMATION"
        self.eur_max_estimate = "EUR_MAX_ESTIMATION"
        self.estimate = "ESTIMATE"
        self.item_result = "FINAL_RESULT"
        self.result = "RESULT"
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
        self.id_auction = "AUCTION_ID"

        # RUN INFO
        self.date_creation = "date_creation"
        self.embedding = "embedding"
        self.distance = "distance"
        self.executed_time = "DATE_EXECUTION"
        self.category = "OBJECT_CATEGORY"
        self.prompt_description = "PROMPT"
        self.prompt_schema = "prompt_schema"
        self.gpt_answer = "answer"
        self.input = "input"
        self.date_run = "date_run"
        self.list_id_item = "list_id_item"

        # clustering variable
        self.cluster_id = "label"
        self.cluster_top_words = "labels_top_words"


class Artists:
    def __init__(self):
        self.artist_family_name = "ARTIST_FAMILY_NAME"
        self.artist_surname = "ARTIST_SURNAME"
        self.artist_year_born = "ARTIST_YEAR_BORN"
        self.artist_year_death = "ARTIST_YEAR_DEATH"


# date format
DATE_FORMAT = "%Y-%m-%d"
DATE_HOUR_FORMAT = "%Y-%m-%d %H:%M:%S"

# for data cleaning
currencies = "USD|CAD|GBP|CHF|EUR|MAD|JPY|AED|MXN|CZK|PLN|CNY|HKD|NLG|AUD|ESP|SGD|DEM|ITL|INR|FRF|TWD|RMB|TRY|SEK|ZAR"
LOCALISATION = "London|New York|Hong Kong|Paris|Geneva|Milan|Amsterdam|Zurich|Toronto|Dubai|Doha|Beijing|Mumbai|Derbyshire|Miami|Palm Beach|Chatsworth|Tel Aviv|Singapore|San Francisco|Monaco"

FIXED_EUR_RATE = {
    "NLG": 1 / 2.20371,
    "FRF": 1 / 6.55957,
    "ITL": 1 / 1936.27,
    "ESP": 1 / 200,
    "DEM": 0.511292,
    "MAD": 0.091,
}  # former currencies before euro

LIST_CURRENCY_PAIRS = [
    "USDEUR",
    "GBPEUR",
    "CHFEUR",
    "SEKEUR",
    "INREUR",
    "PLNEUR",
    "CADEUR",
    "AEDEUR",
    "HKDEUR",
    "SGDEUR",
    "MADEUR",
    "AUDEUR",
    "CNYEUR",
    "JPYEUR",
    "TWDEUR",
    "TRYEUR",
    "ZAREUR",
]

# for steps
list_sellers = ["sothebys", "drouot", "christies", "millon"]

# unique IDS
ID_TEXT = "id_item"
ID_PICTURE = "id_picture"

# naming of features
PICTURE_DB = "picture_embeddings"
TEXT_DB_EN = "text_embeddings_english"
TEXT_DB_FR = "text_embeddings_french"

# URL PICTURE EXCLUDED
BLACK_LIST_ID_PICTURE = [
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "42cc6c83d5aa547a97d8a6ba8422892e3c738c9ecdf53291e1c120cb502ca917",
    "24c080393d0b8fddc7b39f7ac83adcddcfc3e005f00216a131ff5930bcd78ffa",
    "6bee8656dac4093fa90853962dfa70a3dbc4a2e7c2dc8b1c55d179403b640efb",
    "03f9047537bd64dd229f0a722f7bc41c547e01e6dfb09938ce93d2ae8be95431",
    "6244e100a4a3208af52bf97743373b1905bcb71dcea61d0601d65d8abf50ee69",
    "8768b236a2cbe05177e3dfc05e91e002e66b91212493290ab85f51b660f1dc05",
    "12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126",
    "68ee09a0d0c5d4881437212dde9b5986a29a39a76ccc847caf72781a1c91401b",
    "768d59c3e71fb00cf1ee2c379095f102a2b34e0e2df515f08a4542204276d028",
    "374e13de158e92de952c42fae5b8fdfe9b3c3df27bd48e7f9b88b1b181ef2d03",
]

# millon date format to english
MAP_MONTH = {
    "JAN": "JANVIER",
    "FÉV": "FÉVRIER",
    "MAR": "MARS",
    "AVR": "AVRIL",
    "MAI": "MAI",
    "JUIN": "JUIN",
    "JUN": "JUIN",
    "JUIL": "JUILLET",
    "AOÛ": "AOÛT",
    "SEP": "SEPTEMBRE",
    "OCT": "OCTOBRE",
    "NOV": "NOVEMBRE",
    "DÉC": "DÉCEMBRE",
}

# words to remove
LISTE_WORDS_REMOVE = [
    "--> ce lot se trouve au depot",
    ".",
    "",
    "cb",
    "aucune désignation",
    "withdrawn",
    "pas de lot",
    "no lot",
    "retiré",
    "pas venu",
    "40",
    "lot retiré",
    "20",
    "test",
    "300",
    "non venu",
    "--> ce lot se trouve au depôt",
    "hors catalogue",
    "()",
    "1 ^,,^^,,^",
    "estimate",
    "sans titre",
    "untitled",
    "2 ^,,^^,,^",
    "3 ^,,^^,,^",
    "1 ^,,^",
    "6 ^,,^",
    "4 ^,,^",
    "5 ^,,^",
    ".",
    "",
    " ",
    ". ",
    "aucune désignation",
    "retrait",
    "2 ^,,^",
    "3 ^,,^",
    '1 ^"^^"^',
    "1 ^,,^^,,^ per dozen",
    "5 ^,,^^,,^",
    "4 ^,,^^,,^",
    "10 ^,,^^,,^",
    "--> ce lot se trouve au depot",
    "pas de lot",
    "withdrawn",
    "lot non venu",
]
