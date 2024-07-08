docker-compose stop postgres
docker-compose rm postgres
docker-compose down -v
docker-compose build --no-cache
docker-compose up
