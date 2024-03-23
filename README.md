# hart

## Objectifs 

Objectif est de créer un commissaire priseur à partir de l'IA. Ceci aura lieu en plusieurs étapes. 

### Projet 1 : Trend detector - Analytics 

Donner la possibilité d'étudier les évolutions de prix d'artistes & etc. au cours du temps et de la géographie via un dashboard interactif. 

### Projet 2 : Aide à l'estimation pour CP 

En fonction du text et des images donner une estimation de prix avec un intervalle de confiance ainsi que des critères prédits qui permettent de donner une telle évaluation 

### Projet 3 : Arbitrage 

Outil qui identifie toutes les ventes futures et liste les meilleurs opportunités en terme de prix d'achat vs prix annoncé: B2C pour mieux bidder. 

### Projet 4 : CP 

Outil qui à partir de plusieurs photos détermine : 
- la catégorie de l'objet 
- son prix potentiel
- les caractéristiques qui ont permis de déduire le prix annoncé


## Cahier des charges : 
### Crawling - constitution d'une bdd complete 

1.1. Historique a compléter
- Sothebys Level 2&3: crawl les /buy (2000 auctions) & les urls de redirection (1000 auctions)
- Sothebys Level 2: crawl les images manquantes (50%)
- Drouot Level 2 : crawl les pdfs des ventes manquantes + cleaning 
- Drouot Level 3: crawl infos & cleaning

### Infos extraction 

Infos extraites :
- Prix final 
- Prix estimé 
- pays 
- ville
- date 

Extraire les infos suivantes : 
- catégorie de l'objet à partir du text / image - classification 
- Auteur / artiste si disponible - regex / manuel  - seq to seq
- année de la pièce / circa - regex / manuel  - seq to seq
- état de la pièce / objet - regex / manuel  - seq to seq
- existance d'une signature ou non de l'objet / d'un écusson - regex - seq to seq
- taille de l'objet / poids de l'objet - seq to seq
- matériau / type de surface etc. - regex - seq to seq 
- disponibilité des papiers de possession / identification que c'est un vrai 

RAG à développer à partir des embeddings :
- uniquement text 
- text + image en indépendant 
- text & image conjoint en layer mlp (fully connected)
- ensembling d'embeddings si possible