#!/bin/bash
# launch front end - react front
# cd ./webapp-art-analytics
# npm run start &

# launch middle api  - flask api for front management
# cd ../api-art-analytics
# docker-compose up &

# llaunch bakc - embeddings / AI
# cd ../backend-api
# docker-compose up &

# launch S3 equivalent - pictures availability
cd D:/data
python -m http.server 4000 &

# # launch chroma db
# cd ../backend-art-analytics - vectorDB
# chroma run --path "D:/data/chroma_db/chroma_data" &
