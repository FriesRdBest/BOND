# Foundation implementation record

## Scope

This foundation introduces typed immutable catalog values, repository contracts,
deterministic synthetic fixtures, initial maturity rules, explicit telemetry
calculations, design tokens, and automated tests.

A Streamlit interface, persistent workflow, database schema, restricted runtime
role, API routes, and deployment are not established by this batch.

## Runtime

Python 3.12 is the project baseline. The local default Python installation is
not replaced. uv manages the environment and records resolved dependencies in
uv.lock. requirements.txt is exported for deployment tooling. Application
dependencies have bounded source constraints and exact resolved lock entries.

## Scoring decision

The initial three rules check assigned ownership, visible contract evidence,
and absence of reported critical vulnerabilities. They have equal weight.
Unknown evidence remains in the score denominator and never counts as a pass.
Evidence coverage is reported separately. An empty evaluation has no score.

This is a demonstration policy, not a claim about Cortex policy definitions.
Freshness enforcement and versioned persisted evaluations remain future work.

## Fixture semantics

The catalog is synthetic and deterministic. Its observation time is fixed.
Do not represent it as current production telemetry. Dependencies reference
existing services. Fixtures contain no credentials or personal customer data.

## Telemetry decisions

P95 uses nearest rank over the supplied finite nonnegative samples. An empty
sample has no P95. Credit burn is credits per hour using Decimal arithmetic.
Credits are not converted to currency.

## Database check

The connection script uses environment variables, verified TLS, and read only
queries. It never prints credentials or raw connection error messages.
A successful run proves authentication for that environment at that time.
It does not prove restricted runtime permissions or application readiness.

## Verification status

Run the checks and record their actual output. This document does not claim
that checks passed merely because their implementation exists.

## Supabase certificate trust decision

The first Codespaces connection attempt failed certificate validation when using the public certifi CA bundle. DNS and TCP checks passed. Successful database authentication was not established by that attempt.

The connection check now explicitly trusts the packaged public Supabase database root certificate while retaining verify-full. The certificate is public trust material, not a password or private key. It was retrieved over verified HTTPS from the following source:

https://supabase-downloads.s3-ap-southeast-1.amazonaws.com/prod/ssl/prod-ca-2021.crt

Reference guidance:

https://supabase.com/docs/guides/platform/ssl-enforcement

Certificate identity, validity, and SHA256 fingerprint are inspected during setup. Review the certificate before replacing it and monitor expiry. Do not bypass hostname or certificate verification to resolve a connection failure.

Through a pooler, pg_stat_ssl describes the pooler connection to PostgreSQL. Client certificate verification separately protects the application connection to the pooler.

## Typed presentation boundary

Strict checking identified unresolved PyArrow types in Streamlit's broad data signatures. Pandas stubs resolved the pandas definitions. Additional Arrow stubs resolved the class names but left an unspecified Array generic.

BOND uses a narrow presentation adapter for its supported table rows and numeric chart series. Callable protocols describe the arguments actually used. Explicit casts are confined to the external rendering boundary. They are assumptions, not runtime validation of the library implementation.

Forwarding tests, signature checks, and Streamlit page execution tests support this boundary. No project wide diagnostic suppression, source exclusion, or installed library modification is introduced. The unused experimental Arrow stub dependency is removed. Review this boundary when upgrading Streamlit or expanding supported data inputs.
