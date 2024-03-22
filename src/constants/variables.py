
# for crawling & cleaning steps : naming
class Naming:
    def __init__(self):
        self.seller = "SELLER"
        self.auction_infos = "AUCTION_INFOS"
        self.item_infos = "ITEM_INFOS"
        self.item_description = "ITEM_DESCRIPTION"
        self.detailed_description = "DETAIL_DESCRIPTION"

        self.auction_title = "AUCTION_TITLE"
        self.item_title = "ITEM_TITLE"

        self.lot = 'LOT_NUMBER'
        self.type_sale = "TYPE_SALE"
        self.house = "HOUSE"
        self.place = "PLACE"

        self.url_detail = "URL_DETAIL"
        self.url_full_detail = "URL_FULL_DETAILS"
        self.url_auction = "URL_AUCTION"
        self.url_item = "URL_ITEM"
        self.url_picture = "URL_PICTURE"

        self.min_estimate = "MIN_ESTIMATION"
        self.max_estimate = "MAX_ESTIMATION"
        self.brut_estimate = "BRUT_ESTIMATE"
        self.brut_result = "BRUT_RESULT"
        self.item_result = "FINAL_RESULT"
        self.is_item_result = "IS_FINAL_RESULT"

        self.localisation = "LOCALISATION"
        self.currency = "CURRENCY"
        self.date = "AUCTION_DATE"
        self.hour = "AUCTION_HOUR"

        self.auction_file = "AUCTION_FILE"
        self.item_file = "ITEM_FILE"
        self.detail_file = "DETAIL_FILE"

        self.id_picture = "ID_PICTURE"
        self.id_item = "ID_ITEM"
        self.id_auction = "AUCTION_ID"

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
                                    "INFOS" :self.item_infos,
                                    "FILE" : self.item_file, 
                                    "DESCRIPTION": self.item_description}}
    
    def dict_rename_detail(self):
        return {**self.root_dict, **{"URL" : self.url_detail,
                                    "DETAIL" : self.detailed_description,
                                    "TITLE" : self.item_title,
                                    "DESCRIPTION": self.detailed_description,
                                    "FILE" : self.detail_file}}

#for data cleaning
currencies = 'USD|CAD|GBP|CHF|EUR|MAD|JPY|AED|MXN|CZK|PLN|CNY|HKD|NLG|AUD|ESP|SGD|DEM|ITL|INR|FRF|TWD|RMB'
localisation = "London|New York|Hong Kong|Paris|Geneva|Milan|Amsterdam|Zurich|Toronto|Dubai|Doha|Beijing|Mumbai|Derbyshire|Miami|Palm Beach|Chatsworth|Tel Aviv|Singapore|San Francisco|Monaco"

# for steps 
list_sellers = ["sothebys", "drouot", "christies"]

#for feature extraction 
category = ["lithographie", "estampe", "serigraphie",
            "montre", "cuillere", "sculpture",
            "scenes d intérieur","bijoux","boucle d oreille",
            "boucles d oreille","bague","tabatiere","epee",
            "robe longue","plat ovale","fermoir",
            "dague","stylo","pendants d oreilles","gourmette",
            "boucles doreille","robe du soir","huilier","bibelot",    
            "pendentif","fauteuil", "fourchette", "broderie","aiguiere",
            "legumier","verseuse","laitiere","theiere","portes-couteau",
            "broche","medaille","tableau", "plaque", 
            "banette","candelabre","chandelier","sauciere","calice",
            "aquarelle", "huile sur toile","huile sur panneau","acrylique",
            "portrait","flambeau","gueridon","poignard","pot a lait",
            "rond de serviette", "coquetier","porteclefs","pendule","gousset",
            "luminaire", "service à", "tirage argentique",
            "argenterie", "photo", "chaise", "table", "amulette",
            "rond de serviette","jatte","bonbonniere","assiette",
            "pelle a tarte","portemonnaie","dessous de plat",
            "paniere a pain","coffret", "pince a sucre","seau a champagne",
            "collier", "violon", "couteau", "cierge","gobelet",
            "lampe", "dessin", "gravure", "fusil", "pistolet", "vase ",
            "sucrier", "appliques","insignes","porte-carte",
            "couverts","buffet","encrier","shaker","carafon",
            "verres à pied","cafetière","icône","timbale","timballe",
            "scènes d extérieur","affiche","pochoir","présentoir",
            "boite","bouilloire","pendulette","bougeoir",
            "flute a champagne","bas reliefs","hallebarde",
            "louche","plateau","sautoir","ceinture","plat rond",
            "meuble", "bouteille", "cuiller", "tasse",
            "pièce","moutardier", "salière", "bracelet",
            " sac ","coupe", "canne","alliance","pince a",
            "coupe en cristal","vases ","sabre",
            "etui"]

materiau = ["bois", "bronze", "métal argenté",  "papier",
            "ceramique", "porcelaine", "cuivre","saphir", "rubis",
            "soierie",  "toile", "faïence","pierre", "argent",
            "diamant", "verre"]
 
classes = ["monnnaie", "tableau", "gravure", "vin", "photographie", "lithographie", "timbale", "vase", 
           "vêtement", "skateboard", "montre", "bague", "collier", "boucle d'oreille", "bracelet",
           "pendentif", "diamant", "livre", "tapis", "autographe", "moteur", "voiture", "sac à main",
           "luminaire", "lit", "table", "chaise", "fauteuil", "canapé", "guéridon", "table basse",
           "table de chevet", "armoire", "comode", "garde meuble", "vaisselier", "arme blanche", "arme à feu",
           "canne", "coupe", "verre", "pendulle", "bougeoir", "coffret", "pince", "seau à champagne",
           "panière", "pelle", "service à thé ou café", "aquarelle", "portrait", "huile sur toile", "huile sur panneau", 
           "acrylique", "candelabre", "broderie", "tapisserie", "bibelot", "robe", "tabatière", "bonbonnière",
           "sculpture", "instrument de musique", "miroir", "console", "icône", "documents", "canne", 
           "salière", "huilier ou vinaigrier", "médaille", "masque", "antiquité", "applique", "affiche",
           "figurine", "assiette", "plat ou plateau"]