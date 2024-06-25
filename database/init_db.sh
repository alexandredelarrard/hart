#!/bin/bash
set -e

# Clean up any pre-existing shared memory segments
# for shmid in $(ipcs -m | grep -E "0x" | awk '{print $2}'); do
#   ipcrm -m $shmid
# done

# # Ensure the data directory is clean before initializing
# if [ "$(ls -A /var/lib/postgresql/data)" ]; then
#   echo "Cleaning up existing data directory..."
#   rm -rf /var/lib/postgresql/data/*
# fi

# # Initialize the database directory only if it's empty
# if [ -z "$(ls -A /var/lib/postgresql/data)" ]; then
#   echo "Initializing database directory..."

#   # Create a temporary password file
#   echo "$POSTGRES_PASSWORD" > /tmp/pwfile

#   initdb -D /var/lib/postgresql/data --auth-local=scram-sha-256 --auth-host=scram-sha-256 --pwfile=/tmp/pwfile

#   # Ensure proper permissions
#   chown -R postgres:postgres /var/lib/postgresql/data

#   # Remove the temporary password file
#   rm /tmp/pwfile
# fi

# # Start the PostgreSQL server on the specified port
# pg_ctl -D /var/lib/postgresql/data -o "-c listen_addresses='*' -c port=$POSTGRES_PORT" -w start

# Wait for PostgreSQL to be ready
# until pg_isready -h localhost -p $POSTGRES_PORT; do
#   echo "Waiting for PostgreSQL to be ready on port $POSTGRES_PORT..."
#   sleep 2
# done

# Set the PostgreSQL password
# export PGPASSWORD=$POSTGRES_PASSWORD

# Create the user and database
# escaped_password=$(printf '%s\n' "$POSTGRES_PASSWORD" | sed 's/'\''/''\'\''/g')
# psql -U postgres -p $POSTGRES_PORT -c "ALTER USER $POSTGRES_USER WITH PASSWORD '$escaped_password';"
# psql -U postgres -p $POSTGRES_PORT -tc "SELECT 1 FROM pg_database WHERE datname = 'vectordb'" | grep -q 1 || psql -U postgres -p $POSTGRES_PORT -c "CREATE DATABASE vectordb OWNER $POSTGRES_USER TEMPLATE template0 LC_COLLATE 'C' LC_CTYPE 'C'"

# Run the init.sql script to set up the database schema and extensions
# psql -U $POSTGRES_USER -p $POSTGRES_PORT -d vectordb -f /docker-entrypoint-initdb.d/init.sql

# Load data from CSV into picture_embeddings table
# if [ -f /tmp/picture_embeddings.csv ]; then
#   echo "Loading data from /tmp/picture_embeddings.csv into picture_embeddings table..."
#   head -n 101 /tmp/picture_embeddings.csv | psql -U $POSTGRES_USER -d vectordb -p $POSTGRES_PORT -c "\COPY picture_embeddings(ID_UNIQUE, ID_PICTURE, pict_path, CREATED_AT, EMBEDDING) FROM '/tmp/picture_embeddings.csv' DELIMITER ',' CSV HEADER;"
# fi

# Restore the database
# if [ -f /tmp/vectordb_dump.sql ]; then
#   echo "Restoring the database from /tmp/vectordb_dump.sql..."
#   pg_restore -U $POSTGRES_USER -d vectordb -p $POSTGRES_PORT -v /tmp/vectordb_dump.sql
# fi

# Stop the PostgreSQL server
# pg_ctl -D /var/lib/postgresql/data -m fast -w stop
