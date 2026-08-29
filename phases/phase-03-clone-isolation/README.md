# Phase 3 — Clone and isolation

Create `GARAGE_PRIVATE_TEAM_A` as a zero-copy clone of the validated
`GARAGE_PROD` template. Capture object inventories, row counts, view behavior,
and grants before and after cloning. Change data and create one team-only object
in the clone, then prove the source remains unchanged.

Do not assume the database container inherited source grants. Test the actual
result, and remember that child-object grant behavior differs from the cloned
container's grants.

Checkpoint: explain why a clone is an independent point-in-time copy rather
than a synchronized replica, and identify what must be reconciled after clone
creation.
