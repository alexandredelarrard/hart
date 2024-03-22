#for data cleaning
currencies = 'USD|CAD|GBP|CHF|EUR|MAD|JPY|AED|MXN|CZK|PLN|CNY|HKD|NLG|AUD|ESP|SGD|DEM|ITL|INR|FRF|TWD|RMB'
localisation = "London|New York|Hong Kong|Paris|Geneva|Milan|Amsterdam|Zurich|Toronto|Dubai|Doha|Beijing|Mumbai|Derbyshire|Miami|Palm Beach|Chatsworth|Tel Aviv|Singapore|San Francisco|Monaco"

# for steps 
sellers = ["sothebys", "drouot", "christies"]

# for crawling & cleaning steps : 


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