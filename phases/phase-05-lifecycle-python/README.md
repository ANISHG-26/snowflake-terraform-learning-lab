# Phase 5 — Lifecycle automation with Python

Convert the manual clone workflow into a guarded Python command. Begin with a
dry run that prints the exact source, target, account, role, and intended
actions. Require deterministic naming and an explicit disposable marker before
replacement can occur.

The workflow will create or replace a private sandbox, reconcile required
grants, run the Phase 2 validation suite against the clone, and report a
sanitized result. It must clearly warn that team-created data and objects can
be lost. Do not schedule destructive refresh in this phase.

Checkpoint: demonstrate a safe retry and explain failure handling between
replacement, grant reconciliation, and validation.
