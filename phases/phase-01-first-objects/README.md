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

## Checkpoint 3 — Create and load the RAW table

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
