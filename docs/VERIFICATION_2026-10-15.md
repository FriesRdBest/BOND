# Verification record: October 15, 2026

This record captures the technical verification completed after commit
`9d87862`. It does not include owner visual acceptance, which remains a
separate later review.

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

## Boundary

These results verify the inspected local and live technical paths. They do not
establish production capacity, continuous hosted availability, complete
accessibility compliance, or owner visual acceptance.
