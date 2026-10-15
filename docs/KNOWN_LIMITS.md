# Known limits and remaining verification

## Current application mode

The Streamlit interface and API read deterministic synthetic fixtures.
The database schema and PostgreSQL catalog adapter were verified separately
through operator commands. The public interface does not use administrative
database credentials.

## Workflow

Approval, simulated execution, independent verification, and public session
isolation remain to be implemented. The initial audit event table does not
constitute a completed audit workflow.

## Security

The restricted runtime role and its allowed operations remain to be created
and tested before deployment. Row security being enabled does not establish
that privileged operator reads are isolated.

The client database connection passed certificate and hostname verification.
The separate pooler to PostgreSQL link was not reported as TLS. Do not describe
every connection as encrypted.

## Interface

The current native Streamlit shell is a foundation. Purposeful React and
TypeScript components remain phase two work. One desktop Scorecard screenshot
has been reviewed. Full responsive, keyboard, screen reader, and reduced
motion behavior remain to be verified.

## Automated checks

The recorded foundation run passed 57 tests. AppTest checks execution, not
rendered browser accessibility. The local disclosure guard is a small scoped
check, not a comprehensive secret scanner.

The dependency audit reported no known vulnerabilities at the recorded run.
This is not a security certification.

## Maintenance

The test suite currently emits a Starlette TestClient deprecation warning.
Resolve it through a reviewed compatible dependency or test integration change.
Do not hide it with a broad warning filter.

The dedicated dependency audit export should be improved to use hashes where
supported. Preserve the separate deployment export requirements.

## Delivery

Docker configuration exists but its build has not been verified.
GitHub workflow files exist but their execution results must be checked after
push. Streamlit Community Cloud deployment is pending.

Free hosting may sleep, pause, or impose resource limits. No continuous
availability or production capacity claim has been established.
