# Learning notes

This public log records sanitized predictions, experiments, results, and
explanations. Account identifiers and credentials remain local and ignored.

## Phase 0 — Setup and safe connection

### Experiment

Ran the read-only session identity query in Snowsight and through the Python
connector using an ignored `.env` configuration.

### Result

- Active role for this learning run: `SYSADMIN`.
- Active warehouse: `COMPUTE_WH`.
- Python connection succeeded.
- No Snowflake resources were created or modified.

### What I learned

`CURRENT_ROLE()` identifies the active privilege set for the session. A
warehouse provides compute for queries and is separate from stored database
objects. Local `.env` and `.venv/` content must remain outside Git.

## Phase 1 — Garage data foundation

### 1. Synthetic relational data

Generated five deterministic fictional CSV files:

| File/table | Rows |
|---|---:|
| `MANUFACTURERS` | 5 |
| `DEALERSHIPS` | 20 |
| `VEHICLES` | 300 |
| `INVENTORY` | 300 |
| `SERVICE_RECORDS` | 300 |

The dependency order is manufacturers and dealerships, then vehicles, then
inventory and service records.

### 2. Snowflake object foundation

Created `GARAGE_PROD` with `RAW` and `ANALYTICS` schemas, an internal stage, a
named CSV file format, and five explicitly typed landing tables. The table
definitions use `VARCHAR`, fixed-point `NUMBER`, and `DATE` types.

Primary and foreign keys document intended relationships on these standard
tables, but Snowflake does not enforce them. Explicit queries provide the
quality proof.

### 3. Staging and loading

Uploaded all five files to `RAW.GARAGE_CSV_STAGE`, confirmed them with `LIST`,
and loaded them with `COPY INTO ... ON_ERROR = 'ABORT_STATEMENT'`. Row counts
matched the source files.

Repeating a load for an already-recorded filename processed zero files and did
not add duplicate rows. This demonstrated Snowflake load history, not general
data reconciliation.

### 4. Data-quality validation

Duplicate-key, orphan-relationship, null, and domain-value checks returned no
violations. This separates declared schema intent from verified data quality.

### 5. Curated analytics interface

Created `ANALYTICS.SERVICE_HISTORY`, joining service records, vehicles, and
manufacturers. The view exposes a consumer-friendly query without storing a
second independent copy of the result.

### 6. Scoped roles and grants

Created two custom account roles:

- `GARAGE_LOADER`: warehouse/database/raw-schema access, stage `READ`, file
  format `USAGE`, and raw-table `SELECT`/`INSERT` for the direct load pattern.
- `GARAGE_READER`: warehouse/database/analytics-schema access and `SELECT` on
  the approved analytics view only.

Roles were assigned explicitly to the learner's user after creation.

### 7. Least-privilege tests

Disabled secondary roles before testing each custom role:

- `GARAGE_READER` successfully queried `SERVICE_HISTORY` and was denied access
  to `RAW.SERVICE_RECORDS`.
- `GARAGE_LOADER` successfully queried the raw manufacturers table and was
  denied access to the analytics view.

The authorization failures were expected test successes. They proved the
roles' separation instead of relying on privileges from another active role.

### Phase 1 conclusion

The complete flow is local CSV → internal stage → file format → typed raw table
→ quality check → curated view → scoped role. The database remains available
as the candidate template for Phase 2.

## Current checkpoint

- Phase 0: complete.
- Phase 1: complete.
- Phase 2: next — baseline and validate `GARAGE_PROD` as a clone-ready template.

## Workshop checkpoint template

### Prediction

### Experiment

### Result

### Explanation

### Cleanup

### Open questions
