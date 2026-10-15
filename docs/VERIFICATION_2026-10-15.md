# Verification record: October 15, 2026

This record captures the technical and hosted verification completed after commit
`9d87862`. Owner visual acceptance remains a separate later review.

## Local quality gates

| Check | Result |
| --- | --- |
| Python tests | 113 passed, with one recorded FastAPI test client deprecation warning. |
| Ruff format | 57 files already formatted. |
| Ruff lint | All checks passed. |
| Pyright | Zero errors, warnings, and informations. |
| Focused application, workflow, and API tests | 26 passed in 0.47 seconds. |

## Live Supabase verification

| Check | Result |
| --- | --- |
| Database authentication | Passed. |
| Client TLS with certificate and hostname verification | Passed. |
| Read only health query | Passed. |
| Pooler to PostgreSQL transport | Not reported as TLS; retained as a security review observation. |
| Restricted role identity | Verified. |
| Application session scoped workflow | Verified. |
| Row level security isolation without SQL session filters | Verified. |
| Cross session insertion denial | Verified. |
| Migration metadata access denial | Verified. |
| Audit update and delete privilege denial | Verified. |
| PostgreSQL atomic, authorization, and persistence tests | 16 passed. |

The security audit found row level security policies on all six inspected
tables, no public or API role table grants, and 15 grants for the restricted
`bond_app` role. This is verification evidence, not a security certification.

## Interface and browser verification

| Check | Result |
| --- | --- |
| Frontend installation | 115 packages installed; zero vulnerabilities reported. |
| Frontend build | Packaged component assets built with source and output checksums. |
| Frontend contract tests | 6 passed. |
| Production dependency audit | Zero vulnerabilities reported. |
| Explorer bridge, contract, event, and query navigation tests | 24 passed. |
| Accessibility implementation | Focus visible styles, reduced motion handling, semantic landmarks, live status regions, and labeled controls are present. |

## Container and performance verification

| Check | Result |
| --- | --- |
| Docker image build | Passed. |
| Image digest | `sha256:347d1c9b0aafea683db76387734ebc89ee842fa38421a4bab4ebdf378f775695`. |
| Image size | 833,350,091 bytes. |
| Focused test duration | 0.47 seconds for 26 tests. |

## Hosted PostgreSQL verification

Commit `6686c07` enabled the hosted Streamlit application to select durable
PostgreSQL workflow storage when restricted `BOND_DB_*` settings are supplied.
Without those settings, it retains the in memory demonstration mode.

The hosted demonstration was verified in private browser sessions:

| Check | Result |
| --- | --- |
| Hosted application startup | Passed after a transient Streamlit dependency download failure was resolved by rebooting the application. |
| Restricted runtime credentials | Configured privately in Streamlit secrets; not shared with reviewers. |
| Complete workflow | A recommendation was proposed, approved, executed as a simulated action, and verified successfully. |
| Audit history | Proposal, approval, simulated execution, and verification events were recorded. |
| PostgreSQL durability | The completed workflow and its events remained present in the `bond.improvements` and `bond.workflow_events` tables. |
| Refresh isolation | A hard refresh began a new demonstration session and did not display the prior session’s workflow. |
| Cross session isolation | A second private browser session could not see the first session’s recommendation or audit history. |
| Separate workflow state | Each session retained its own recommendation state and event history. |

The database contained distinct session identifiers for the completed and
separate proposed workflows. This confirms durable storage with demonstration
session isolation.

## Phase status

With hosted PostgreSQL durability and session isolation verified, phases one
through four are complete. Phase five is complete for the current technical
submission: the Streamlit application is deployed, restricted runtime
credentials are configured, a fresh hosted reviewer session was tested, the
durable PostgreSQL mode decision was implemented and verified, documentation
and community standards are present, and main protection and required checks
are enabled.

Future visual upgrades are enhancement work, not a blocker for the current
submission.

## Boundary

These results verify the inspected local, live database, and hosted technical
paths. They do not establish production capacity, continuous hosted
availability, complete accessibility conformance, or owner visual acceptance.
