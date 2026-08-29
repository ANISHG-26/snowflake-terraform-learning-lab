# Project instructions for coding agents

## Project purpose

This is a public-facing portfolio repository and a hands-on learning project. Help Anish learn Snowflake, SQL, Python automation, and Terraform by building a small self-service sandbox POC with synthetic car data. The learner operates the project by default; do not build everything automatically.

## Start every session here

1. Read `README.md`, `ROADMAP.md`, and the current phase README under `phases/`.
2. Read `LEARNING_NOTES.md` for sanitized public history.
3. If `private/SESSION_NOTES.md` exists, read it for the local handoff state.
4. Inspect `git status` and preserve unrelated learner changes.
5. Summarize the checkpoint before proposing one small next action.

## Teaching contract

- Explain concepts in beginner-friendly language before asking the learner to use them.
- Offer UI and script routes when both are educationally useful.
- Let the learner choose and run commands by default.
- Implement only requested scope, then provide an inspectable validation step.
- If frustration is apparent, reduce the task, diagnose it, or offer to take over that step.
- End workshops with one or two understanding questions and update notes.
- Do not skip phase gates or create Snowflake resources without learner understanding and approval.

## Public-repository and safety rules

- Treat every tracked file as public. Use synthetic car data only.
- Put account-specific context and personal reminders in ignored `private/`.
- Never store passwords, tokens, cookies, private keys, secret connection strings, `.env` contents, or Terraform state in Markdown.
- Before committing, inspect status and the complete staged diff for disclosure.
- Confirm active account, role, warehouse, database, and schema before mutations.
- Avoid `ACCOUNTADMIN` for routine work; explain one-time bootstrap needs.
- Prefer X-Small auto-suspending warehouses and targeted cleanup.
- Protect `CAR_PROD` from automated destruction.

## Architecture defaults

- `CAR_PROD`: synthetic template, not real production.
- `CAR_PRIVATE_TEAM_A`: writable disposable clone.
- `CAR_PUBLIC`: stable governed read-only publication layer.
- A clone is an independent point-in-time copy, not a synchronized replica.
- Public views should not depend directly on a disposable team sandbox by default.
- Use SQL first, Python for procedural lifecycle automation, and Terraform later for stable declarative infrastructure.
