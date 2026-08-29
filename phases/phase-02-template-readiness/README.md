# Phase 2 — Template readiness

## Outcome

Turn the completed `GARAGE_PROD` database into a template we can clone with
confidence. Phase 1 already built the data model, so this workshop focuses on
quality evidence, useful analytics, and predictable reload behavior rather
than adding tables for their own sake.

## Why this phase exists

A clone faithfully copies the source at a point in time. If the source is
incorrect or poorly understood, cloning only reproduces that problem faster.
Before creating `GARAGE_PRIVATE_TEAM_A`, we will define what “template ready”
means and produce a validation result that Python can check.

## Checkpoint 1 — Baseline the template

Inspect session identity, object inventory, row counts, constraints, stage
contents, view definition, and grants. Save sanitized expected values in a
small validation specification; do not capture account identifiers.

Prediction: standard-table primary and foreign keys document relationships but
do not prove data integrity. Our validation queries provide that proof.

## Checkpoint 2 — Create reusable quality checks

Move the Phase 1 checks into visible SQL and a small Python validation runner:

- expected row counts;
- duplicate business keys;
- nulls in required fields;
- orphan relationships;
- accepted fuel types and inventory statuses;
- future service dates and negative costs.

The runner should report every check, return a non-zero exit code on failure,
and never mutate Snowflake.

## Checkpoint 3 — Introduce one controlled failure

Use a transaction or temporary test table to introduce one bad row, predict
which check will fail, observe it, and roll back or remove only the test object.
Do not damage the validated template to demonstrate a failure.

## Checkpoint 4 — Add two useful analytics views

Create small consumer-oriented views such as monthly service cost by
manufacturer and inventory by region/status. Define the question each view
answers before writing SQL and avoid exposing raw columns without a use case.

## Checkpoint 5 — Learn rerun versus reconcile

Run the existing bootstrap without changing its input and observe Snowflake's
file-load behavior. Then discuss what would happen if a CSV changed while its
filename stayed the same.

Key distinction:

- **rerunnable:** repeating the same operation does not create duplicate data;
- **reconciling:** automation detects and applies differences to reach a
  declared desired state.

The Phase 1 bootstrap is intentionally the first kind, not the second.

## Completion gate

Phase 2 is complete when:

- one command can validate the template without modifying it;
- an intentional quality failure is detected and safely cleaned up;
- the analytical views answer stated business questions;
- you can explain why same-name staged files and load history complicate refresh behavior;
- a final validation run passes immediately before cloning.

## Understanding questions

1. Why do declared primary and foreign keys not replace quality checks here?
2. What is the difference between a rerunnable bootstrap and reconciliation?
