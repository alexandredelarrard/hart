#!/bin/bash

# Initialize the database
airflow db init

# Create admin user
airflow users create \
    --username $AIRFLOW_ADMIN_USER \
    --password $AIRFLOW_ADMIN_PASSWORD \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email $AIRFLOW_ADMIN_EMAIL

# Keep the container running
exec "$@"
