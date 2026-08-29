# Snowflake Sandbox Terraform POC

A guided, public portfolio project for learning Snowflake, SQL, Python automation, and Terraform by building a small self-service data platform for a synthetic garage business.

```text
CAR_PROD (synthetic template)
    +-- point-in-time clone --> CAR_PRIVATE_TEAM_A (writable, disposable)
    +-- approved interface --> CAR_PUBLIC (read-only curated views)
```

## How we work

Each phase supports a Snowsight UI path, a small script path, and assisted implementation when explicitly requested. The learner operates by default. Before any command, we explain the objective, expected result, cost/destructive implications, and cleanup.

## Start here

1. Open [Phase 0](phases/phase-00-setup/README.md).
2. Work through one checkpoint at a time.
3. Record sanitized observations in [LEARNING_NOTES.md](LEARNING_NOTES.md).
4. Use [ROADMAP.md](ROADMAP.md) as the course index.
5. Use [SNOWFLAKE_WIKI.md](SNOWFLAKE_WIKI.md) as the running concept reference.

## Public and private context

Tracked files must remain portfolio-safe. Account-specific observations and session handoffs go under ignored `private/`. Credentials, private keys, tokens, Terraform state, and credential profiles never belong in Markdown. Review `git status` and the staged diff before publishing.

## Current status

- Python 3.12, Terraform 1.8.4, and Git are installed.
- Snowflake CLI was not found during the initial check.
- Phase 0 complete: Python made a successful read-only Snowflake connection.
- No Snowflake resources have been created or modified.
- Next: Phase 1 — create the first small Snowflake objects after reviewing the safety and cost implications.
