# Learning roadmap

Each phase is a self-contained workshop. The sequence moves from visible manual work to automation only after the underlying Snowflake behavior has been observed.

| Phase | Workshop | Outcome | Status |
|---|---|---|---|
| 0 | [Setup and safe connection](phases/phase-00-setup/README.md) | Check tools and inspect session context without creating objects | Complete |
| 1 | [Garage data foundation](phases/phase-01-garage-foundation/README.md) | Generate five related CSVs, load `GARAGE_PROD`, validate it, and practice scoped grants | Complete |
| 2 | [Template readiness](phases/phase-02-template-readiness/README.md) | Turn the garage into a validated, clone-ready template and learn controlled reload behavior | Next |
| 3 | [Clone and isolation](phases/phase-03-clone-isolation/README.md) | Clone and prove isolation | Not started |
| 4 | [RBAC and publication](phases/phase-04-rbac-publication/README.md) | Evolve basic roles into ownership, team, and governed publication boundaries | Not started |
| 5 | [Lifecycle automation](phases/phase-05-lifecycle-python/README.md) | Build a guarded Python create/replace/expiry workflow | Not started |
| 6 | [Terraform and self-service](phases/phase-06-terraform-self-service/README.md) | Manage stable infrastructure and validate declarative sandbox requests | Not started |
| 7 | [Scheduling and final review](phases/phase-07-scheduling-review/README.md) | Schedule safe lifecycle behavior, rebuild the POC, and present the portfolio story | Not started |

Workshop loop: learn → predict → choose UI/script → run one task → inspect → record → checkpoint.
