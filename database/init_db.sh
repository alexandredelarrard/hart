#!/bin/bash
set -e

# Start the PostgreSQL server on port 5433
pg_ctl -D "$PGDATA" -o "-c listen_addresses='*' -c port=5433" -w start

# Wait for PostgreSQL to be ready
until pg_isready -h localhost -p 5433; do
  echo "Waiting for PostgreSQL to be ready on port 5433..."
  sleep 2
done

# Restore the database
if [ -f /tmp/vectordb_dump.sql ]; then
  echo "Restoring the database from /tmp/vectordb_dump.sql..."
  pg_restore -U postgres -d postgres -v /tmp/vectordb_dump.sql
fi

# Stop the PostgreSQL server
pg_ctl -D "$PGDATA" -m fast -w stop