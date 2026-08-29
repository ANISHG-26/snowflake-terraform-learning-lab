# Snowflake learning wiki

This is a quick memory aid for the synthetic garage project. It is not a
replacement for the workshop checkpoints or Snowflake documentation.

## The garage mental model

```text
Account       = the whole garage company/account
Warehouse     = the engine that runs queries
Database      = the garage building
Schema        = a room in the building
Stage         = the receiving dock for files
File format   = instructions for reading a delivery
Table         = an organized filing cabinet
View          = a window showing selected information
Role          = a staff access badge
Grant         = a permission written onto that badge
```

## Core concepts

### Warehouse

A virtual warehouse supplies compute for SQL statements. It is separate from
stored data. Suspending a warehouse pauses compute and cost; it does not delete
tables or databases.

### Database

A database is a top-level container for schemas and objects. This project uses
`GARAGE_PROD` as a fictional production-style database.

### Schema

A schema is a namespace or room inside a database. `RAW` is our landing room;
`ANALYTICS` is our curated reporting room.

### Stage

A stage stores files before loading. An internal stage is managed by Snowflake;
an external stage points to cloud storage such as Amazon S3, Azure Blob, or
Google Cloud Storage. A stage does not define table columns and does not clean
the data. Internal stages use `READ` and `WRITE` privileges rather than
database-style `USAGE`: `READ` supports listing/reading staged files, while
`WRITE` supports uploading or removing files.

### File format

A file format is a reusable parsing rulebook for staged files. It can describe
CSV delimiters, header rows, quotes, escapes, null markers, compression, and
other file details.

```sql
CREATE FILE FORMAT GARAGE_CSV_FORMAT
  TYPE = CSV
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"';
```

For pipe-delimited data, use `FIELD_DELIMITER = '|'`.

### Table

A table stores rows and columns. Our `RAW` tables use explicit types such as
`VARCHAR`, `NUMBER(10,2)`, and `DATE`. Primary and foreign keys document intent;
we still run validation queries for duplicates and orphan references.

### View

A view stores a query definition, not a second physical copy of the result.
It can provide a safer interface by exposing selected columns and rows from
underlying tables.

### Role and grant

A role is a named collection of privileges. A grant assigns a privilege on an
object to a role. Common privileges in this project:

- `USAGE`: allows using a database, schema, warehouse, or similar object;
- `SELECT`: allows reading rows from a table or view;
- `INSERT`/`UPDATE`/`DELETE`: allow changing table data;
- `OWNERSHIP`: controls the object and can grant or revoke privileges.

Snowflake access usually requires privileges at each relevant level. For
example, reading a view commonly requires database `USAGE`, schema `USAGE`,
and `SELECT` on the view.

Snowflake sessions can also use secondary roles. With secondary roles set to
`ALL`, privileges from every role granted to the user may contribute to an
operation. This can make a restricted-role test misleading. Use
`USE SECONDARY ROLES NONE` when testing one role in isolation, then verify with
`CURRENT_ROLE()` and `CURRENT_SECONDARY_ROLES()`.

System roles have different jobs. `USERADMIN` normally creates users and
custom roles. `SYSADMIN` normally creates warehouses, databases, schemas, and
other database objects. `SECURITYADMIN` commonly manages grants. A role can be
given the account-level `CREATE ROLE` privilege when an administrator
deliberately wants it to create roles.

## Parsing versus cleaning

These are related but different:

```text
Stage       stores the file
File format parses its structure
COPY INTO   loads fields into table columns
SQL         validates or transforms values
```

Useful cleaning functions include `TRIM`, `UPPER`, `LOWER`, `NULLIF`,
`TRY_TO_NUMBER`, and `TRY_TO_DATE`. `TRY_` conversions return `NULL` instead
of failing for an invalid value, which can be useful during controlled
validation.

## Useful inspection commands

```sql
SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();
SHOW DATABASES;
SHOW SCHEMAS IN DATABASE GARAGE_PROD;
SHOW STAGES IN SCHEMA GARAGE_PROD.RAW;
SHOW FILE FORMATS IN SCHEMA GARAGE_PROD.RAW;
SHOW TABLES IN SCHEMA GARAGE_PROD.RAW;
SHOW VIEWS IN SCHEMA GARAGE_PROD.ANALYTICS;
SHOW GRANTS TO ROLE GARAGE_READER;
```

## Loading vocabulary

- `PUT`: uploads a local file to an internal stage; commonly used from a client
  such as SnowSQL or a Python connector.
- `COPY INTO <table>`: loads staged files into a table using a file format.
- `LIST @stage`: shows files currently in a stage.
- `VALIDATION_MODE`: can help inspect load errors before committing rows.

Loading with `COPY INTO` requires the loader role to have access to the named
file format and, for this direct table-load pattern, `SELECT` and `INSERT` on
the target table. This means the simple `GARAGE_LOADER` role is a controlled
raw read/write role, not a write-only role. A more restrictive production
pattern could isolate ingestion behind a procedure or service identity.

## Project object map

```text
GARAGE_PROD
├── RAW
│   ├── GARAGE_CSV_STAGE
│   ├── GARAGE_CSV_FORMAT
│   ├── MANUFACTURERS
│   ├── DEALERSHIPS
│   ├── VEHICLES
│   ├── INVENTORY
│   └── SERVICE_RECORDS
└── ANALYTICS
    └── SERVICE_HISTORY
```

## Questions to test understanding

1. If a warehouse is suspended, what remains available?
2. Which object controls comma versus pipe parsing?
3. Why might a reader receive `SELECT` on a view but not on a raw table?
