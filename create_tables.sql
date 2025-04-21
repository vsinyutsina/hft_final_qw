CREATE DATABASE airflow_db;

CREATE DATABASE airflow_meta;

CREATE DATABASE superset_meta;

\c airflow_db

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'bluepilled') THEN
        CREATE USER bluepilled with password '';
END IF;
END $$;

GRANT ALL PRIVILEGES ON DATABASE airflow_meta TO bluepilled;

ALTER DATABASE airflow_meta OWNER TO bluepilled;

GRANT ALL PRIVILEGES ON DATABASE superset_meta TO bluepilled;

ALTER DATABASE superset_meta OWNER TO bluepilled;

GRANT ALL PRIVILEGES ON DATABASE airflow_db TO bluepilled;

ALTER DATABASE airflow_db OWNER TO bluepilled;

CREATE SCHEMA IF NOT EXISTS dwh_raw AUTHORIZATION bluepilled;

CREATE TABLE IF NOT EXISTS dwh_raw.timeseries_shares (
                                                         share_name varchar(10),
    ticker_name varchar(10),
    datetime timestamp,
    open numeric(10, 2),
    high numeric(10, 2),
    low numeric(10, 2),
    close numeric(10, 2),
    volume int
    );
ALTER TABLE dwh_raw.timeseries_shares OWNER TO bluepilled;

CREATE TABLE IF NOT EXISTS dwh_raw.calendar (
                                                datetime timestamp
);
ALTER TABLE dwh_raw.calendar OWNER TO bluepilled;