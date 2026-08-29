# Learning notes

## Phase 0 inventory

- Python 3.12.0, Terraform 1.8.4, and Git installed.
- Snowflake CLI not found.
- No Snowflake resources changed.

## Phase 0 completion

### Prediction

The Python connection should report the same active role and warehouse as
Snowsight.

### Experiment

Used the Phase 0 Python connector script with local environment settings from
`.env`. The script ran the read-only session identity query.

### Result

- Active role: `SYSADMIN`
- Active warehouse: `COMPUTE_WH`
- Python connection: successful
- Snowflake resources created or modified: none

### Explanation

`CURRENT_ROLE()` reports the role active in the current session. That role is
important because its granted privileges determine which Snowflake operations
the session can perform. The warehouse identifies the compute context used by
queries; it is separate from stored data.

### Cleanup

No Snowflake cleanup was needed. Local `.env` and `.venv/` remain ignored by
Git.

### Open questions

- Which objects can `SYSADMIN` create in the next phase?
- What warehouse size and auto-suspend settings are appropriate for a small
  learning project?

## Initial mental model and decisions

- Snowflake storage and warehouse compute are separate.
- A zero-copy clone is a writable, independent point-in-time copy; it does not synchronize.
- Clone grants must be inspected rather than guessed.
- A view stores a query definition, so its dependencies affect lifecycle design.
- Use `CAR_PUBLIC` for the read-only layer and “sandbox” for disposable writable environments.
- Learn one table and view before the full model; introduce Terraform after direct SQL, cloning, and RBAC.

## Phase 1 progress — garage foundation

### Checkpoint: first typed table

#### Prediction

`RAW.MANUFACTURERS` should contain three required text columns, with
`manufacturer_id` documented as the primary key.

#### Experiment

Created and inspected `GARAGE_PROD.RAW.MANUFACTURERS` in Snowsight using the
Phase 1 DDL.

#### Result

The table contains:

- `MANUFACTURER_ID VARCHAR(10)`
- `MANUFACTURER_NAME VARCHAR(100)`
- `COUNTRY VARCHAR(60)`

No account-specific details or credentials were recorded.

#### Explanation

This is a reference table with no foreign-key dependencies, so it is the first
table in the planned load order. Explicit column types make the expected shape
clear before CSV data is loaded.

#### Cleanup

No cleanup performed; this table is part of the Phase 1 garage database.

#### Open questions

- How will `DEALERSHIPS` differ from `MANUFACTURERS` even though both are reference tables?
- Which table will depend on `MANUFACTURERS`?

### Checkpoint: second reference table

#### Experiment

Created and inspected `GARAGE_PROD.RAW.DEALERSHIPS` in Snowsight.

#### Result

The table contains `DEALERSHIP_ID VARCHAR(10)`, `DEALERSHIP_NAME
VARCHAR(120)`, and `REGION VARCHAR(60)`. Both reference tables now exist in
the `RAW` schema.

#### Explanation

`DEALERSHIPS` is independent reference data, so it can be created before the
tables that refer to it. The Snowflake object listing also shows the database
and table names, while `DESC TABLE` shows the column definitions.

#### Cleanup

No cleanup performed.

### Checkpoint: staged garage files

#### Experiment

Uploaded the five generated CSV files to `GARAGE_CSV_STAGE` and verified them
with `LIST` in Snowsight.

#### Result

The stage contains `manufacturers.csv`, `dealerships.csv`, `vehicles.csv`,
`inventory.csv`, and `service_records.csv`. The files are ready for loading;
no files were deleted from the stage.

#### Explanation

The stage is the file landing area. The file format already defines how the
comma-delimited headers and values should be parsed, while the target tables
define the Snowflake data types.

#### Cleanup

No cleanup performed.

### Checkpoint: raw data loaded

#### Experiment

Loaded the five staged CSV files into the matching `RAW` tables with
`COPY INTO` and `ON_ERROR = 'ABORT_STATEMENT'`.

#### Result

The loaded row counts match the generated files:

| Table | Rows |
|---|---:|
| `MANUFACTURERS` | 5 |
| `DEALERSHIPS` | 20 |
| `VEHICLES` | 300 |
| `INVENTORY` | 300 |
| `SERVICE_RECORDS` | 300 |

#### Explanation

The file format parsed the CSV structure, while the destination table
definitions converted the fields into Snowflake types such as `NUMBER` and
`DATE`. Loading reference data before dependent data keeps the process aligned
with the business dependency graph.

#### Cleanup

No cleanup performed; staged files were retained for repeatability.

### Checkpoint: raw garage table layer

#### Experiment

Created and inspected the five typed landing tables in
`GARAGE_PROD.RAW`: `MANUFACTURERS`, `DEALERSHIPS`, `VEHICLES`, `INVENTORY`,
and `SERVICE_RECORDS`.

#### Result

All five tables appear in the database with the planned `VARCHAR`, `NUMBER`,
and `DATE` columns. The dependency intent is manufacturers and dealerships,
then vehicles, then inventory and service records.

#### Explanation

The raw layer now defines the expected shape of the garage data before any CSV
rows are loaded. Keys document relationships, while later validation queries
will check duplicates, nulls, and orphan references.

#### Cleanup

No cleanup performed.

## Checkpoint template

### Prediction

### Experiment

### Result

### Explanation

### Cleanup

### Open questions
