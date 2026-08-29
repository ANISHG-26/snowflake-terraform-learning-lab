# Phase 4 — RBAC and governed publication

Phase 1 introduced isolated loader and reader roles. This phase evolves that
foundation into platform ownership, team sandbox access, and a stable
`GARAGE_PUBLIC` publication layer that does not depend directly on a disposable
team clone.

Test each role with secondary roles disabled and capture both allowed and
expected-denied operations. Compare object ownership, database/schema `USAGE`,
table/view `SELECT`, future grants, and the grants retained or omitted during
cloning.

Checkpoint: explain `OWNERSHIP`, `USAGE`, `SELECT`, role hierarchy, and why the
public interface should survive replacement of a private sandbox.
