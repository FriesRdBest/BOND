# Known limits and remaining verification

## Current application mode

The Streamlit interface and API read deterministic synthetic fixtures.
The database schema and PostgreSQL catalog adapter were verified separately
through operator commands. The public interface does not use administrative
database credentials.

## Workflow

The recommendation, approval, simulated execution, verification, and audit
history workflow is implemented for synthetic evidence. Its public interface
uses an in memory demonstration store unless PostgreSQL mode is explicitly
selected.

The PostgreSQL workflow migration is applied and verified. The restricted
runtime role and public hosted session isolation remain deployment work.

## Security

The restricted runtime role and its allowed operations remain to be created
and tested before deployment. Row security being enabled does not establish
that privileged operator reads are isolated.

The client database connection passed certificate and hostname verification.
The separate pooler to PostgreSQL link was not reported as TLS. Do not describe
every connection as encrypted.

## Interface

The React and TypeScript evidence explorer is implemented and packaged with
the Streamlit application. Its inspection bridge, keyboard interaction,
native fallback, visible label pointer interaction, narrow catalog
containment, and scoped automated accessibility scan passed browser tests.

Owner visual review of the phase two interface is pending. The browser scan
does not establish full application accessibility or every responsive layout.

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

The dedicated application audit now uses hashed requirements and completed
successfully in the recorded phase two check. The deployment export remains
separate because it includes the editable local package.

## Delivery

Docker configuration exists but its build has not been verified.
GitHub workflow files exist but their execution results must be checked after
push. Streamlit Community Cloud deployment is pending.

Free hosting may sleep, pause, or impose resource limits. No continuous
availability or production capacity claim has been established.
