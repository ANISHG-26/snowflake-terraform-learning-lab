"""Idempotently bootstrap the synthetic garage database.

Credentials come from the existing environment/.env settings. This script
creates and loads the Phase 1 objects; review it before running in a new
account. It does not drop or replace objects.
"""

from __future__ import annotations

import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv


ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DATABASE = "GARAGE_PROD"
RAW = f"{DATABASE}.RAW"
ANALYTICS = f"{DATABASE}.ANALYTICS"
STAGE = f"{RAW}.GARAGE_CSV_STAGE"
FORMAT = f"{RAW}.GARAGE_CSV_FORMAT"


def setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def connect(role: str) -> snowflake.connector.SnowflakeConnection:
    options = {
        "user": setting("SNOWFLAKE_USER"),
        "password": setting("SNOWFLAKE_PASSWORD"),
        "account": setting("SNOWFLAKE_ACCOUNT"),
        "role": role,
    }
    if os.getenv("SNOWFLAKE_WAREHOUSE"):
        options["warehouse"] = os.environ["SNOWFLAKE_WAREHOUSE"]
    return snowflake.connector.connect(**options)


def execute(role: str, statements: list[str]) -> None:
    with connect(role) as connection, connection.cursor() as cursor:
        for statement in statements:
            print(f"[{role}] {statement.splitlines()[0]}")
            cursor.execute(statement)


def main() -> None:
    load_dotenv()
    # USERADMIN owns account role creation in the default Snowflake hierarchy.
    execute("USERADMIN", [
        "CREATE ROLE IF NOT EXISTS GARAGE_LOADER",
        "CREATE ROLE IF NOT EXISTS GARAGE_READER",
    ])

    execute("SYSADMIN", [
        f"CREATE DATABASE IF NOT EXISTS {DATABASE}",
        f"CREATE SCHEMA IF NOT EXISTS {RAW}",
        f"CREATE SCHEMA IF NOT EXISTS {ANALYTICS}",
        f"CREATE STAGE IF NOT EXISTS {STAGE}",
        f"""CREATE FILE FORMAT IF NOT EXISTS {FORMAT}
TYPE = CSV FIELD_DELIMITER = ',' SKIP_HEADER = 1
FIELD_OPTIONALLY_ENCLOSED_BY = '"' EMPTY_FIELD_AS_NULL = TRUE
NULL_IF = ('', 'NULL', 'null')""",
        f"""CREATE TABLE IF NOT EXISTS {RAW}.MANUFACTURERS (
manufacturer_id VARCHAR(10) NOT NULL, manufacturer_name VARCHAR(100) NOT NULL,
country VARCHAR(60) NOT NULL,
CONSTRAINT pk_manufacturers PRIMARY KEY (manufacturer_id))""",
        f"""CREATE TABLE IF NOT EXISTS {RAW}.DEALERSHIPS (
dealership_id VARCHAR(10) NOT NULL, dealership_name VARCHAR(120) NOT NULL,
region VARCHAR(60) NOT NULL,
CONSTRAINT pk_dealerships PRIMARY KEY (dealership_id))""",
        f"""CREATE TABLE IF NOT EXISTS {RAW}.VEHICLES (
vehicle_id VARCHAR(10) NOT NULL, manufacturer_id VARCHAR(10) NOT NULL,
model VARCHAR(80) NOT NULL, model_year NUMBER(4,0) NOT NULL,
fuel_type VARCHAR(20) NOT NULL, color VARCHAR(30) NOT NULL,
price_usd NUMBER(10,2) NOT NULL,
CONSTRAINT pk_vehicles PRIMARY KEY (vehicle_id),
CONSTRAINT fk_vehicles_manufacturer FOREIGN KEY (manufacturer_id)
REFERENCES {RAW}.MANUFACTURERS (manufacturer_id))""",
        f"""CREATE TABLE IF NOT EXISTS {RAW}.INVENTORY (
inventory_id VARCHAR(10) NOT NULL, vehicle_id VARCHAR(10) NOT NULL,
dealership_id VARCHAR(10) NOT NULL, status VARCHAR(20) NOT NULL,
CONSTRAINT pk_inventory PRIMARY KEY (inventory_id),
CONSTRAINT fk_inventory_vehicle FOREIGN KEY (vehicle_id) REFERENCES {RAW}.VEHICLES (vehicle_id),
CONSTRAINT fk_inventory_dealership FOREIGN KEY (dealership_id) REFERENCES {RAW}.DEALERSHIPS (dealership_id))""",
        f"""CREATE TABLE IF NOT EXISTS {RAW}.SERVICE_RECORDS (
service_id VARCHAR(10) NOT NULL, vehicle_id VARCHAR(10) NOT NULL,
service_type VARCHAR(40) NOT NULL, service_date DATE NOT NULL,
cost_usd NUMBER(10,2) NOT NULL,
CONSTRAINT pk_service_records PRIMARY KEY (service_id),
CONSTRAINT fk_service_vehicle FOREIGN KEY (vehicle_id) REFERENCES {RAW}.VEHICLES (vehicle_id))""",
        f"""CREATE OR REPLACE VIEW {ANALYTICS}.SERVICE_HISTORY AS
SELECT s.service_id, s.vehicle_id, m.manufacturer_name, v.model, v.model_year,
v.fuel_type, s.service_type, s.service_date, s.cost_usd
FROM {RAW}.SERVICE_RECORDS s JOIN {RAW}.VEHICLES v ON s.vehicle_id = v.vehicle_id
JOIN {RAW}.MANUFACTURERS m ON v.manufacturer_id = m.manufacturer_id""",
        "GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE GARAGE_LOADER",
        "GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE GARAGE_READER",
        f"GRANT USAGE ON DATABASE {DATABASE} TO ROLE GARAGE_LOADER",
        f"GRANT USAGE ON DATABASE {DATABASE} TO ROLE GARAGE_READER",
        f"GRANT USAGE ON SCHEMA {RAW} TO ROLE GARAGE_LOADER",
        f"GRANT USAGE ON SCHEMA {ANALYTICS} TO ROLE GARAGE_READER",
        f"GRANT READ ON STAGE {STAGE} TO ROLE GARAGE_LOADER",
        f"GRANT USAGE ON FILE FORMAT {FORMAT} TO ROLE GARAGE_LOADER",
        f"GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA {RAW} TO ROLE GARAGE_LOADER",
        f"GRANT SELECT ON VIEW {ANALYTICS}.SERVICE_HISTORY TO ROLE GARAGE_READER",
    ])

    with connect("SYSADMIN") as connection, connection.cursor() as cursor:
        for filename in ("manufacturers.csv", "dealerships.csv", "vehicles.csv", "inventory.csv", "service_records.csv"):
            local_file = (DATA_DIR / filename).resolve().as_posix()
            cursor.execute(f"PUT 'file://{local_file}' @{STAGE} AUTO_COMPRESS=FALSE OVERWRITE=FALSE")
            table = filename.removesuffix(".csv").upper()
            cursor.execute(f"COPY INTO {RAW}.{table} FROM @{STAGE}/{filename} FILE_FORMAT=(FORMAT_NAME='{FORMAT}') ON_ERROR='ABORT_STATEMENT'")
            print(f"Loaded {filename}")

    print("Garage bootstrap complete. Assign roles to a user separately with SECURITYADMIN.")


if __name__ == "__main__":
    main()
