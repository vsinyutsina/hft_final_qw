#!/usr/bin/env bash
set -eo pipefail

pip install yfinance

# initdb
airflow db upgrade

# Wait for PostgreSQL to be ready (initial check)
until PGPASSWORD= pg_isready -U bluepilled -h postgres -d airflow_meta; do
  echo "Waiting for PostgreSQL to be ready (initial check)..."
  sleep 2
done

# Delay before starting Airflow Scheduler
echo "Waiting for PostgreSQL to restart..."
sleep 10  # <--- Adjust this value as needed

# Wait for PostgreSQL to be ready (after restart)
until PGPASSWORD= pg_isready -U bluepilled -h postgres -d airflow_meta; do
  echo "Waiting for PostgreSQL to be ready (after restart)..."
  sleep 2
done

if ! airflow users list | grep -q "admin"; then
    airflow users create \
        --username admin \
        --firstname Airflow \
        --lastname Admin \
        --role Admin \
        --email admin@example.com \
        --password 
fi

if ! airflow connections list | grep -q "postgres_hse"; then
    airflow connections add postgres_hse \
        --conn-type postgres \
        --conn-host postgresql \
        --conn-port 5432 \
        --conn-login bluepilled \
        --conn-password \
        --conn-extra '{"dbname": "airflow_db"}'
fi

exec airflow standalone