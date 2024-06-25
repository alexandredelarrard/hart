#!/bin/bash
set -e

# Run the init.sql script to set up the database schema and extensions
psql -U $POSTGRES_USER -p $POSTGRES_PORT -d vectordb -f /tmp/init.sql

# Restore the database
if [ -f /tmp/vectordb_dump.sql ]; then
  echo "Restoring the database from /tmp/vectordb_dump.sql..."
  pg_restore -U $POSTGRES_USER -d vectordb -p $POSTGRES_PORT -v /tmp/vectordb_dump.sql
fi

