# Quick bootstrap guide

Use this guide to recreate the synthetic garage environment in a fresh
Snowflake trial account.

## What this creates

- Database: `GARAGE_PROD`
- Schemas: `RAW`, `ANALYTICS`
- Internal stage: `RAW.GARAGE_CSV_STAGE`
- CSV file format: `RAW.GARAGE_CSV_FORMAT`
- Five raw tables and one analytics view
- Roles: `GARAGE_LOADER`, `GARAGE_READER`
- Five synthetic CSV uploads and their table loads

The script is non-destructive and safely rerunnable for the supplied dataset:
it uses `IF NOT EXISTS`, does not drop objects, and does not assign roles to a
user. It is not a general reconciliation engine: changed table definitions are
not migrated, existing staged filenames are not overwritten, and Snowflake can
skip filenames already recorded in load history.

## Prerequisites

1. Python 3.12 or newer.
2. The Snowflake connector and dotenv package installed in the active virtual environment:

   ```powershell
   python -m pip install snowflake-connector-python python-dotenv
   ```

3. An existing `COMPUTE_WH`, or another warehouse named in
   `SNOWFLAKE_WAREHOUSE`.
4. A user that can use `USERADMIN` and `SYSADMIN`.

The default Snowflake role separation matters: `USERADMIN` creates roles and
`SYSADMIN` creates database objects. If your account uses a custom arrangement,
adjust the role names in the script only after understanding the privileges.

## Configure credentials safely

Create an ignored local `.env` file in the repository root. Never commit it or
paste its contents into chat.

```text
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
```

The script reads these values through `python-dotenv`. Do not put passwords,
tokens, private keys, or connection strings in tracked Markdown or Python.

## Run the bootstrap

From the repository root:

```powershell
python phases/phase-01-garage-foundation/generate_vehicles.py
python phases/phase-01-garage-foundation/setup_garage.py
```

The first command regenerates the five deterministic CSV files. The second
command creates the Snowflake objects, uploads the files, and runs `COPY INTO`
in dependency order.

## Verify the result

In Snowsight, run:

```sql
SHOW DATABASES LIKE 'GARAGE_PROD';
SHOW SCHEMAS IN DATABASE GARAGE_PROD;
SHOW TABLES IN SCHEMA GARAGE_PROD.RAW;
SHOW VIEWS IN SCHEMA GARAGE_PROD.ANALYTICS;

SELECT 'MANUFACTURERS' AS table_name, COUNT(*) AS row_count FROM GARAGE_PROD.RAW.MANUFACTURERS
UNION ALL SELECT 'DEALERSHIPS', COUNT(*) FROM GARAGE_PROD.RAW.DEALERSHIPS
UNION ALL SELECT 'VEHICLES', COUNT(*) FROM GARAGE_PROD.RAW.VEHICLES
UNION ALL SELECT 'INVENTORY', COUNT(*) FROM GARAGE_PROD.RAW.INVENTORY
UNION ALL SELECT 'SERVICE_RECORDS', COUNT(*) FROM GARAGE_PROD.RAW.SERVICE_RECORDS;
```

Expected counts are 5, 20, 300, 300, and 300.

## Assign roles explicitly

The bootstrap script creates roles and object grants but deliberately does not
assign them to a user. As `SECURITYADMIN`, replace the placeholder with the
exact username from `SELECT CURRENT_USER()`:

```sql
USE ROLE SECURITYADMIN;

GRANT ROLE GARAGE_READER TO USER YOUR_USERNAME;
GRANT ROLE GARAGE_LOADER TO USER YOUR_USERNAME;
```

For isolated testing:

```sql
USE SECONDARY ROLES NONE;
USE ROLE GARAGE_READER;
```

## Troubleshooting

- `CREATE ROLE` denied: switch to `USERADMIN`, or use a role with account-level `CREATE ROLE`.
- Internal stage rejects `USAGE`: use `READ` and/or `WRITE`; internal stages do not use `USAGE`.
- File format not authorized: grant `USAGE` on `GARAGE_CSV_FORMAT` to the loader role.
- `COPY INTO` needs table access: the direct load pattern requires `SELECT` and `INSERT` on the target table.
- Reader can access raw data: run `USE SECONDARY ROLES NONE` and verify `CURRENT_ROLE()`.
- A repeated load reports 0 files processed: Snowflake recognized the staged file as already loaded.

## Safety and cleanup

Review the script before running it in a new account. It does not destroy
objects, but it does create database resources and may incur storage or
warehouse usage. Suspend the warehouse when finished. Do not drop
`GARAGE_PROD` until you have reviewed the later clone and RBAC exercises.
