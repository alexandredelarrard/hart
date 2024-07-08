#!/bin/bash
set -e

# Extract the tar file into the PostgreSQL data directory
if [ -f /db_backup/database_pgdata.tar ]; then
  tar -xvf /db_backup/database_pgdata.tar -C /var/lib/postgresql/data
  chown -R postgres:postgres /var/lib/postgresql/data
  rm /db_backup/database_pgdata.tar
  echo "extraction done"
fi

# Execute the original entrypoint script
exec /usr/local/bin/docker-entrypoint.sh "$@"
