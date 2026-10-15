# Known limits and remaining verification

## Current application mode

The Streamlit interface and API read deterministic synthetic fixtures.
The database schema and PostgreSQL catalog adapter were verified separately
through operator commands. The public interface does not use administrative
database credentials.

## Workflow

The recommendation, approval, simulated execution, verification, and audit
history workflow is implemented for synthetic evidence.

When restricted `BOND_DB_HOST`, `BOND_DB_USER`, and `BOND_DB_PASSWORD`
settings are supplied, the hosted Streamlit application selects PostgreSQL
workflow storage. Without those settings, it uses an in-memory demonstration
store. A missing Streamlit secrets file is handled as memory mode rather than
raising an error.

The PostgreSQL workflow migration, restricted runtime role, hosted session
isolation, atomic persistence, and recovery behavior were verified in the
recorded live database checks.

## Security

Row level security and restricted-role checks provide verification evidence,
not a security certification. Privileged operator access and operational
monitoring remain separate concerns.

The client database connection passed certificate and hostname verification.
The separate pooler to PostgreSQL link was not reported as TLS. Do not describe
every connection as encrypted.

## Interface

The React and TypeScript evidence explorer is implemented and packaged with
the Streamlit application. Its inspection bridge, keyboard interaction,
native fallback, visible label pointer interaction, narrow catalog
containment, and scoped automated accessibility scan passed browser tests.

Owner visual review of the interface remains pending. The browser scan
does not establish full application accessibility or every responsive layout.

## Automated checks

The current recorded Python suite passes 120 tests. AppTest checks execution,
not rendered browser accessibility. The local disclosure guard is a small
scoped check, not a comprehensive secret scanner.

The dependency audit reported no known vulnerabilities at the recorded run.
This is not a security certification.

## Maintenance

The test suite currently emits a Starlette TestClient deprecation warning.
Resolve it through a reviewed compatible dependency or test integration change.
Do not hide it with a broad warning filter.

The dedicated application audit now uses hashed requirements and completed
successfully in the recorded phase two check. The deployment export remains
separate because it includes the editable local package.

## Delivery

Docker configuration exists and its build passed in the recorded verification.
GitHub Quality and Frontend workflows passed in the manually triggered run for
commit `0b4ea47`.

Free hosting may sleep, pause, or impose resource limits. No continuous
availability or production capacity claim has been established.
