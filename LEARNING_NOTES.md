# Learning notes

## Phase 0 inventory

- Python 3.12.0, Terraform 1.8.4, and Git installed.
- Snowflake CLI not found.
- No Snowflake resources changed.

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
