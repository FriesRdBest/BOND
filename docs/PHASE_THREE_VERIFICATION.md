# Phase three verification record

## Recorded local results

The owner supplied terminal output on October 15, 2026 confirming the
following phase three results.

| Check | Recorded result |
| --- | --- |
| Workflow and persistence tests | 16 passed after the idempotency and isolation repairs. |
| Workflow API tests | Four passed, including the complete journey and failure paths. |
| Complete Python suite | 98 passed with one recorded test client deprecation warning. |
| Python formatting and lint | Passed. |
| Strict Python source types | Zero errors and zero warnings. |
| Frontend source types and lint | Passed. |
| Frontend contract tests | Six passed. |
| Frontend dependency audit | Zero vulnerabilities reported for the inspected lock. |
| Real browser checks | Seven passed, including the complete workflow journey. |

## Browser workflow scope

The browser check selected Billing Export through the native service
combobox, proposed an owner assignment recommendation, approved it, recorded
a simulated execution, verified success, and inspected the four resulting
audit events.

The test waits for the selected service render before asserting the workflow
form. This prevents a false failure while Streamlit completes its rerender.

## Workflow policy

Recommendations can be created only from failing or missing evidence for a
known synthetic service. Passing evidence cannot create a recommendation.

The allowed progression is proposed to approved or rejected, approved to
executed, and executed to verified or review required. Every accepted
transition records a distinct event.

A repeated request identifier returns the current recommendation without
creating another event. Cross session recommendation reads return no result,
cross session history returns no events, and direct cross session access
raises a controlled error.

## Persistence boundary

The PostgreSQL migration adds demo sessions, improvements, and workflow
events. It includes foreign keys, status constraints, request idempotency,
indexes, row level security, and revoked public privileges.

The corrected migration was applied and verified before this record was
published. The database now contains the workflow improvement and event
tables, with row level security enabled and public privileges revoked.

Applying the migration does not by itself establish restricted runtime
permissions or hosted session isolation.

## Interface storage mode

The public Streamlit interface uses the in memory demonstration store by
default. This keeps visitor demonstrations isolated within each interface
session without requiring database credentials.

The FastAPI interface also uses the in memory store in its current default
configuration. PostgreSQL mode is implemented and can be selected explicitly
after restricted runtime credentials are configured.

## Remaining acceptance

Owner visual review of the completed phase three workflow is pending.
Hosted acceptance, restricted database credentials, and public hosted
session isolation remain subsequent deployment hardening work.

The Starlette TestClient deprecation warning remains recorded and must be
resolved through a reviewed compatible dependency or test integration change.
