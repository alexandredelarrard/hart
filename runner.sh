cd ./data/chroma_db
chroma run 

python -m src datacrawl step-crawling-detailed -t 5 -s drouot -sqs 500 --text-only True