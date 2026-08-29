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

## Checkpoint template

### Prediction

### Experiment

### Result

### Explanation

### Cleanup

### Open questions
