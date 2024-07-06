#!/bin/bash
set -e

#!/bin/bash
sed -i 's/^ *# *maintenance_work_mem *= *[^ ]*/maintenance_work_mem = 4GB #/' /var/lib/postgresql/data/postgresql.conf
sed -i 's/^ *# *max_parallel_maintenance_workers *= *[^ ]*/max_parallel_maintenance_workers = 4 #/' /var/lib/postgresql/data/postgresql.conf
sed -i 's/^ *# *max_wal_size *= *[^ ]*/max_wal_size = 1GB #/' /var/lib/postgresql/data/postgresql.conf

# Run the init.sql script to set up the database schema and extensions
psql -U $POSTGRES_USER -p $POSTGRES_PORT -d vectordb -f /tmp/init.sql

# # Restore the database
# if [ -f /tmp/vectordb_dump.sql ]; then
#   echo "Restoring the database from /tmp/vectordb_dump.sql..."
#   pg_restore -U $POSTGRES_USER -d vectordb -p $POSTGRES_PORT -v /tmp/vectordb_dump.sql
# fi
