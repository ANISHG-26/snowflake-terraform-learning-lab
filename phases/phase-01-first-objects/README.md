# Phase 1 — Seed a production-shaped database

## Outcome

Start with local, synthetic CSV files; create a small database with clear
schemas; load the files with Python; and protect the objects with a minimal
role and grant model.

This phase is deliberately small, but it treats the database like a real
environment: vehicles arrive for service, work is recorded, and different
staff need different access. We will practice ownership, least-privilege
access, separation between raw and curated data, and inspectable grants. All
records are fictional.

## What we will build

```text
GARAGE_PROD
├── RAW       -- landing tables loaded from CSV
└── ANALYTICS -- curated view(s), initially derived from RAW

Roles:
SYSADMIN     -- setup owner for this learning phase
GARAGE_LOADER -- can load RAW, cannot read ANALYTICS by default
GARAGE_READER -- can read approved ANALYTICS views, not RAW tables
```

`COMPUTE_WH` already exists from Phase 0, so we will not create another
warehouse unless inspection shows that one is needed. A warehouse runs
queries; database objects store and expose data.

## Guardrails before every mutation

1. Confirm the active account, role, warehouse, database, and schema.
2. Use synthetic data and an X-Small, auto-suspending warehouse only.
3. Do not use `ACCOUNTADMIN` for routine work.
4. Preview each SQL statement before running it and inspect the result.
5. Never put credentials, `.env` contents, or connection strings in tracked files.
6. Do not grant broad access such as `ALL PRIVILEGES ON DATABASE` to a reader.

## Checkpoint 1 — Generate and inspect CSVs locally

Create a small repeatable relational dataset outside Snowflake. The generator
creates five CSVs:

- `manufacturers.csv` — 5 vehicle-brand reference rows;
- `dealerships.csv` — 20 garage locations;
- `vehicles.csv` — 300 vehicles;
- `inventory.csv` — 300 vehicle-location/status records;
- `service_records.csv` — 300 garage service records.

The relationships are `vehicles.manufacturer_id`,
`inventory.vehicle_id`/`dealership_id`, and `service_records.vehicle_id`.
The garage story is: a vehicle belongs to a manufacturer, may be held at a
garage location, and can have service work recorded against it. Start by
inspecting `service_records.csv` and `vehicles.csv`.

```text
vehicle_id,make,model,model_year,fuel_type,price_usd
V001,Orion,Trail 2,2022,Hybrid,32000
V002,Maple,City E,2023,Electric,41000
V003,Northstar,Haul 150,2021,Gasoline,28500
```

Before loading, inspect the header, row count, nulls, duplicate `vehicle_id`
values, and whether the values are intentionally synthetic. Prediction: a CSV
is only a file format; it has no Snowflake permissions or schema guarantees.

## Checkpoint 2 — Create the database and schemas

Using Python, create `GARAGE_PROD`, `RAW`, and `ANALYTICS` with idempotent SQL
(`CREATE ... IF NOT EXISTS`). Inspect them with `SHOW DATABASES` and
`SHOW SCHEMAS`. Then explain the difference between a database and schema,
stored data and warehouse compute, and `RAW` versus `ANALYTICS`.

Before writing the table DDL, review [SCHEMA_DESIGN.md](SCHEMA_DESIGN.md).
It records the column types, key intent, dependency graph, load order, and
post-load validation checks.

### Snowsight hands-on route

After confirming the session identity from Phase 0, open a new worksheet and
run only this foundation block:

```sql
CREATE DATABASE IF NOT EXISTS GARAGE_PROD;

CREATE SCHEMA IF NOT EXISTS GARAGE_PROD.RAW;

CREATE SCHEMA IF NOT EXISTS GARAGE_PROD.ANALYTICS;
```

Then inspect the result:

```sql
SHOW DATABASES LIKE 'GARAGE_PROD';
SHOW SCHEMAS IN DATABASE GARAGE_PROD;
```

Expected result: one database and two user-created schemas. Record the active
role and the object names, but do not paste account-specific details into this
repository. Stop here before creating the stage; we will review the result and
then create the ingestion stage as a separate checkpoint.

## Checkpoint 3 — Create the internal ingestion stage

A stage is Snowflake-managed storage used as a landing point for files before
`COPY INTO` loads them into tables. It is not a table and does not define the
columns or data types. For this workshop, create one internal stage inside the
`RAW` schema:

```sql
USE DATABASE GARAGE_PROD;
USE SCHEMA RAW;

CREATE STAGE IF NOT EXISTS GARAGE_CSV_STAGE;

SHOW STAGES IN SCHEMA GARAGE_PROD.RAW;
```

Expected result: one stage named `GARAGE_CSV_STAGE`. In Snowsight, open the
stage from **Data → Databases → GARAGE_PROD → RAW → Stages** and confirm it is
empty. A stage stores files; it does not describe how Snowflake should parse
them.

## Checkpoint 4 — Define the CSV file format

A file format is a reusable parsing rulebook for staged files. It specifies
details such as the delimiter, header row, quoted values, and null handling.
Create one named CSV format:

```sql
USE DATABASE GARAGE_PROD;
USE SCHEMA RAW;

CREATE FILE FORMAT IF NOT EXISTS GARAGE_CSV_FORMAT
  TYPE = CSV
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  EMPTY_FIELD_AS_NULL = TRUE
  NULL_IF = ('', 'NULL', 'null');

SHOW FILE FORMATS IN SCHEMA GARAGE_PROD.RAW;
```

### Load staged CSV files

After verifying the five files with `LIST`, load them in dependency order. Keep
`ON_ERROR = 'ABORT_STATEMENT'` so a bad file does not silently produce a
partial learning result.

```sql
USE DATABASE GARAGE_PROD;
USE SCHEMA RAW;

COPY INTO MANUFACTURERS
FROM @GARAGE_CSV_STAGE/manufacturers.csv
FILE_FORMAT = (FORMAT_NAME = GARAGE_CSV_FORMAT)
ON_ERROR = 'ABORT_STATEMENT';

COPY INTO DEALERSHIPS
FROM @GARAGE_CSV_STAGE/dealerships.csv
FILE_FORMAT = (FORMAT_NAME = GARAGE_CSV_FORMAT)
ON_ERROR = 'ABORT_STATEMENT';

COPY INTO VEHICLES
FROM @GARAGE_CSV_STAGE/vehicles.csv
FILE_FORMAT = (FORMAT_NAME = GARAGE_CSV_FORMAT)
ON_ERROR = 'ABORT_STATEMENT';

COPY INTO INVENTORY
FROM @GARAGE_CSV_STAGE/inventory.csv
FILE_FORMAT = (FORMAT_NAME = GARAGE_CSV_FORMAT)
ON_ERROR = 'ABORT_STATEMENT';

COPY INTO SERVICE_RECORDS
FROM @GARAGE_CSV_STAGE/service_records.csv
FILE_FORMAT = (FORMAT_NAME = GARAGE_CSV_FORMAT)
ON_ERROR = 'ABORT_STATEMENT';

SELECT 'MANUFACTURERS' AS table_name, COUNT(*) AS row_count FROM MANUFACTURERS
UNION ALL SELECT 'DEALERSHIPS', COUNT(*) FROM DEALERSHIPS
UNION ALL SELECT 'VEHICLES', COUNT(*) FROM VEHICLES
UNION ALL SELECT 'INVENTORY', COUNT(*) FROM INVENTORY
UNION ALL SELECT 'SERVICE_RECORDS', COUNT(*) FROM SERVICE_RECORDS;
```

Expected counts are 5 manufacturers, 20 dealerships, and 300 rows in each of
the three operational tables. After the load, run the validation queries in
the next checkpoint before creating the analytics view.

## Checkpoint 6 — Validate the loaded data

```sql
-- Duplicate key checks: each query should return zero rows.
SELECT manufacturer_id, COUNT(*) FROM MANUFACTURERS
GROUP BY manufacturer_id HAVING COUNT(*) > 1;

SELECT dealership_id, COUNT(*) FROM DEALERSHIPS
GROUP BY dealership_id HAVING COUNT(*) > 1;

SELECT vehicle_id, COUNT(*) FROM VEHICLES
GROUP BY vehicle_id HAVING COUNT(*) > 1;

SELECT inventory_id, COUNT(*) FROM INVENTORY
GROUP BY inventory_id HAVING COUNT(*) > 1;

SELECT service_id, COUNT(*) FROM SERVICE_RECORDS
GROUP BY service_id HAVING COUNT(*) > 1;

-- Orphan checks: each query should return zero rows.
SELECT v.vehicle_id FROM VEHICLES v
LEFT JOIN MANUFACTURERS m ON m.manufacturer_id = v.manufacturer_id
WHERE m.manufacturer_id IS NULL;

SELECT i.inventory_id FROM INVENTORY i
LEFT JOIN VEHICLES v ON v.vehicle_id = i.vehicle_id
LEFT JOIN DEALERSHIPS d ON d.dealership_id = i.dealership_id
WHERE v.vehicle_id IS NULL OR d.dealership_id IS NULL;

SELECT s.service_id FROM SERVICE_RECORDS s
LEFT JOIN VEHICLES v ON v.vehicle_id = s.vehicle_id
WHERE v.vehicle_id IS NULL;

-- Domain checks: each query should return zero rows.
SELECT * FROM INVENTORY
WHERE status NOT IN ('IN_STOCK', 'IN_TRANSIT', 'SOLD');

SELECT * FROM VEHICLES
WHERE fuel_type NOT IN ('Gasoline', 'Hybrid', 'Electric', 'Diesel');
```

Do not upload files yet. Inspect the format and confirm that the delimiter is
`,` and the header row is skipped. A pipe-delimited file would use
`FIELD_DELIMITER = '|'` instead.

Cleaning functions are a separate concern: SQL functions such as `TRIM`,
`UPPER`, `TRY_TO_NUMBER`, and `TRY_TO_DATE` transform values during a query or
load. The stage stores files, and the file format parses files; neither one
automatically cleans business data.

## Checkpoint 5 — Create and load the RAW tables

Create five `RAW` tables with explicit Snowflake data types. Load the CSVs
through Python using a narrowly scoped stage and `COPY INTO`. Load reference
tables before dependent tables, then inspect row counts, sample rows, rejected
files, and load history. Decide whether repeat runs replace data or append with
duplicate protection before running the load twice.

## Checkpoint 4 — Add a curated view

Create an approved `ANALYTICS.SERVICE_HISTORY` view joining vehicles and
service records. Expose useful operational columns and demonstrate that a view
stores a query definition, not a second independent copy of the tables.

## Checkpoint 5 — Introduce Snowflake IAM/RBAC

Create two narrowly scoped custom roles:

- `GARAGE_LOADER`: database/schema `USAGE`, plus the minimum table/stage privileges needed to load `RAW`;
- `GARAGE_READER`: database/schema `USAGE`, plus `SELECT` on the approved `ANALYTICS` view only.

Grant roles to your user only when the account permits it and role switching is
understood. Keep `SYSADMIN` as setup owner for now; ownership transfer and a
fuller role hierarchy belong in Phase 4.

Inspect `SHOW GRANTS ON DATABASE`, `SHOW GRANTS ON SCHEMA`, `SHOW GRANTS ON
TABLE`, `SHOW GRANTS ON VIEW`, and `SHOW GRANTS TO ROLE`. Test one allowed and
one deliberately denied operation. A denied permission test is an expected
learning result.

## Completion checkpoint

Phase 1 is complete when you can explain how the CSV became a typed table, why
`RAW` and `ANALYTICS` are separate, and what `USAGE`, `SELECT`, and `OWNERSHIP`
mean at a high level. You should also be able to inspect grants and clean up
without touching `COMPUTE_WH`.

Cleanup is reviewed explicitly. Do not drop `CAR_PROD` or its warehouse
automatically; protect the database until the phase review is complete.

## Choose the route

- **Python-first:** generate/validate the CSV and run numbered SQL statements from a small script.
- **Snowsight-first:** run numbered SQL manually and use Python for CSV validation/loading.

Recommended first action: Python generates and validates `vehicles.csv`; no
Snowflake resources are created in Checkpoint 1.

## Understanding questions

1. Why should a reader role receive `SELECT` on a view instead of broad database access?
2. What happens if the warehouse is suspended while the table still exists?

## Phase 1 command log

This section keeps the runnable Snowsight commands in workshop order.

### Foundation

```sql
CREATE DATABASE IF NOT EXISTS GARAGE_PROD;
CREATE SCHEMA IF NOT EXISTS GARAGE_PROD.RAW;
CREATE SCHEMA IF NOT EXISTS GARAGE_PROD.ANALYTICS;

SHOW DATABASES LIKE 'GARAGE_PROD';
SHOW SCHEMAS IN DATABASE GARAGE_PROD;
```

### Stage and file format

```sql
USE DATABASE GARAGE_PROD;
USE SCHEMA RAW;

CREATE STAGE IF NOT EXISTS GARAGE_CSV_STAGE;
SHOW STAGES IN SCHEMA GARAGE_PROD.RAW;
LIST @GARAGE_CSV_STAGE;

CREATE FILE FORMAT IF NOT EXISTS GARAGE_CSV_FORMAT
  TYPE = CSV
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  EMPTY_FIELD_AS_NULL = TRUE
  NULL_IF = ('', 'NULL', 'null');

SHOW FILE FORMATS IN SCHEMA GARAGE_PROD.RAW;
```

### RAW tables

The complete idempotent table-creation block is recorded below. Run it after
the foundation, stage, and file-format commands.

```sql
USE DATABASE GARAGE_PROD;
USE SCHEMA RAW;

CREATE TABLE IF NOT EXISTS MANUFACTURERS (
    manufacturer_id VARCHAR(10) NOT NULL,
    manufacturer_name VARCHAR(100) NOT NULL,
    country VARCHAR(60) NOT NULL,
    CONSTRAINT pk_manufacturers PRIMARY KEY (manufacturer_id)
);

CREATE TABLE IF NOT EXISTS DEALERSHIPS (
    dealership_id VARCHAR(10) NOT NULL,
    dealership_name VARCHAR(120) NOT NULL,
    region VARCHAR(60) NOT NULL,
    CONSTRAINT pk_dealerships PRIMARY KEY (dealership_id)
);

CREATE TABLE IF NOT EXISTS VEHICLES (
    vehicle_id VARCHAR(10) NOT NULL,
    manufacturer_id VARCHAR(10) NOT NULL,
    model VARCHAR(80) NOT NULL,
    model_year NUMBER(4,0) NOT NULL,
    fuel_type VARCHAR(20) NOT NULL,
    color VARCHAR(30) NOT NULL,
    price_usd NUMBER(10,2) NOT NULL,
    CONSTRAINT pk_vehicles PRIMARY KEY (vehicle_id),
    CONSTRAINT fk_vehicles_manufacturer FOREIGN KEY (manufacturer_id)
        REFERENCES MANUFACTURERS (manufacturer_id)
);

CREATE TABLE IF NOT EXISTS INVENTORY (
    inventory_id VARCHAR(10) NOT NULL,
    vehicle_id VARCHAR(10) NOT NULL,
    dealership_id VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL,
    CONSTRAINT pk_inventory PRIMARY KEY (inventory_id),
    CONSTRAINT fk_inventory_vehicle FOREIGN KEY (vehicle_id)
        REFERENCES VEHICLES (vehicle_id),
    CONSTRAINT fk_inventory_dealership FOREIGN KEY (dealership_id)
        REFERENCES DEALERSHIPS (dealership_id)
);

CREATE TABLE IF NOT EXISTS SERVICE_RECORDS (
    service_id VARCHAR(10) NOT NULL,
    vehicle_id VARCHAR(10) NOT NULL,
    service_type VARCHAR(40) NOT NULL,
    service_date DATE NOT NULL,
    cost_usd NUMBER(10,2) NOT NULL,
    CONSTRAINT pk_service_records PRIMARY KEY (service_id),
    CONSTRAINT fk_service_vehicle FOREIGN KEY (vehicle_id)
        REFERENCES VEHICLES (vehicle_id)
);

SHOW TABLES IN SCHEMA GARAGE_PROD.RAW;
```

### Table inspection

```sql
DESC TABLE GARAGE_PROD.RAW.MANUFACTURERS;
DESC TABLE GARAGE_PROD.RAW.DEALERSHIPS;
DESC TABLE GARAGE_PROD.RAW.VEHICLES;
DESC TABLE GARAGE_PROD.RAW.INVENTORY;
DESC TABLE GARAGE_PROD.RAW.SERVICE_RECORDS;
```
