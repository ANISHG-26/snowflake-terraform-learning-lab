# Phase 0 — Setup and safe connection

## Outcome

Open Snowflake, identify the account and role in use, and make a read-only connection. Do not create databases, warehouses, or roles yet.

## Step 1 — Confirm Snowsight access

Sign into your personal account and locate your username, current role, account identifier/URL, and any warehouse available. Never paste passwords, keys, or session tokens into this repository or chat.

## Step 2 — Run a read-only identity query

In **Projects → Worksheets**, run:

```sql
SELECT
  CURRENT_ORGANIZATION_NAME() AS organization_name,
  CURRENT_ACCOUNT_NAME()      AS account_name,
  CURRENT_USER()              AS user_name,
  CURRENT_ROLE()              AS active_role,
  CURRENT_WAREHOUSE()         AS active_warehouse,
  CURRENT_DATABASE()          AS active_database,
  CURRENT_SCHEMA()            AS active_schema;
```

This changes nothing. `NULL` for warehouse, database, or schema is acceptable. Record only sanitized observations.

## Step 3 — Choose one local route

- **Snowflake CLI:** interactive terminal; requires installing `snow`.
- **Python connector:** smallest local addition because Python exists.
- **Snowsight only:** valid through Phase 1; automation can wait.

Use browser/SSO, an ignored local profile, or carefully configured key-pair authentication. Never hard-code credentials. Avoid `ACCOUNTADMIN` for ordinary work.

## Checkpoint

1. What does `CURRENT_ROLE()` tell you and why does it matter?
2. Which route do you want first?
3. Which authentication method does the account use?

Share a redacted identity result before we create anything.
