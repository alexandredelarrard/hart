# hart

## Objectifs 

Objectif est de créer un commissaire priseur à partir de l'IA. Ceci aura lieu en plusieurs étapes. 

### Projet 1 : Trend detector - Analytics 

Donner la possibilité d'étudier les évolutions de prix d'artistes & etc. au cours du temps et de la géographie via un dashboard interactif avec critères de sélection.

### Projet 2 : Aide à l'estimation pour CP 

En fonction du text et des images donner une estimation de prix avec un intervalle de confiance ainsi que des critères prédits qui permettent de donner une telle évaluation

sur les vases: 
- Baseline 135% hors cas extremes (10, 200 000)
- Erreur de 100% avec toutes les infos dont CP estimate min max 
- Erreur de 400% si juste le text 

### Projet 3 : Arbitrage 

Outil qui identifie toutes les ventes futures et liste les meilleurs opportunités en terme de prix d'achat vs prix annoncé: B2C pour mieux bidder. 

### Projet 4 : CP 

Outil qui à partir de plusieurs photos détermine : 
- la catégorie de l'objet 
- son prix potentiel
- les caractéristiques qui ont permis de déduire le prix annoncé


### Projet 5 : Assurance objets 

Outil qui à partir de plusieurs photos / pdfs / documents : 
- la catégorie de l'objet 
- son prix potentiel / intervalle et la prime en conséquence pour l'assurer
- les caractéristiques qui ont permis de déduire le prix annoncé

## Cahier des charges : 
### Crawling - constitution d'une bdd complete 

1.1. Historique a compléter
- Sothebys Level 2: crawl les /buy (2000 auctions) & les urls de redirection (1000 auctions)
- Sothebys Level 2: crawl les images manquantes (50%)

- Drouot Level 2: crawl les pdfs des ventes manquantes + cleaning 
- Drouot Level 2: missing 0.38M pictures /3.3M items - recrawl them

- Christies level 2 & 3: recrawl SSO urls redirected because only first page was crawled because missing ?loadall=true after rediction (10%)

### Infos extraction 

Infos extraites :
- Prix final 
- Prix estimé 
- pays 
- ville
- date 

A faire : 

RAG à développer à partir des embeddings :
- uniquement text 
- text + image en indépendant 
- text & image conjoint en layer mlp (fully connected)
- ensembling d'embeddings si possible

Modeles :
- detection automatique de signature et nom associé 
- lineage des oeuvers dans le temps / provenance
- extraction des informations du text de manière robuste / JSON - GPT
- Prédire le prix d'une oeuvre à partir de text + image 
- Prédire la description d'une image à partir d'une paire image, text 
- Chatbot qui donne l'estimation d'une oeuvre à travers un chat