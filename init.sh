#!/bin/bash
set -e

# Явные пути к конфигам
PG_CONF="/var/lib/postgresql/data/postgresql.conf"
PG_HBA_CONF="/var/lib/postgresql/data/pg_hba.conf"

# Настройка listen_addresses
if [[ -z "$POSTGRES_HOST_AUTH_METHOD" ]]; then
  sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF"
fi

# Правило с scram-sha-256
if ! grep -q "host    all             bluepilled             0.0.0.0/0            scram-sha-256" "$PG_HBA_CONF"; then
  echo "host    all             bluepilled             0.0.0.0/0            scram-sha-256" >> "$PG_HBA_CONF"
fi

# Перезагрузка конфигурации
pg_ctl reload