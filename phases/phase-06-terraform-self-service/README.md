# Phase 6 — Terraform and self-service

Use Terraform for stable, low-blast-radius platform resources, then represent a
sandbox request as validated configuration. Keep procedural clone replacement
in the guarded Python workflow from Phase 5.

Progress through provider pinning and authentication, state safety, one stable
resource, plans, dependencies, drift, and import before adding roles or grants.
Separate stable platform state from disposable sandbox requests.

Then validate a small YAML request containing name, owner, purpose, warehouse
size, and expiry. Produce a plan-like preview before calling either Terraform
or Python. Invalid or unsafe names and sizes must be rejected without changing
Snowflake.

Checkpoint: identify every create/change/destroy action in a Terraform plan and
explain why a request field belongs to Terraform, Python, or neither.
