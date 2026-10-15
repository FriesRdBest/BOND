# BOND architecture

## Intended boundaries

| Layer | Responsibility |
| --- | --- |
| Presentation | Streamlit shell and purposeful React components written in TypeScript and CSS. |
| Application | Use cases, authorization, transaction coordination, and controlled state transitions. |
| Domain | Immutable values where appropriate, maturity rules, evidence semantics, and verification logic. |
| Contracts | Pydantic input and output validation shared by presentation and API entry points. |
| Repositories | Explicit interfaces for persistence without interface framework dependencies. |
| Adapters | PostgreSQL persistence, deterministic JSON fixtures, and optional Snowflake ingestion. |
| API | Separately runnable FastAPI entry point calling the same application services. |

## Persistence

Supabase PostgreSQL is the durable application store. Version controlled migrations define schema changes. JSON is a local demo and test adapter, not the authority for durable public state. Separate administrative migration access from restricted runtime access.

## Evidence and actions

Record provenance, observation time, applicable rule version, and evaluation outcome. Treat missing evidence explicitly. Separate approval, attempted execution, and verification. Preserve an audit trail and enforce valid transitions transactionally. Design retries so repeated requests do not duplicate actions.

## Public demonstration

Default to deterministic synthetic fixtures. Isolate visitor scenarios through an explicit session or tenant mechanism selected during implementation. Public activity must not modify real infrastructure. Label simulated telemetry and actions at the point of use.

## Telemetry semantics

Distinguish Snowflake warehouse metrics from application database connection pool metrics. State units, sample windows, and freshness. Explain P95 methodology. Do not convert credits to money without a stated pricing assumption. Do not present fixture improvements as observed production savings.

## Portability

Keep environment configuration external, dependencies explicit, migrations reproducible, and domain logic independent of the UI. Docker supports local execution and future deployment. A standalone React frontend remains a future integration effort, not a completed capability.

## Decisions still required

Record selected schema, package versions, role grants, API contracts, state model, session isolation, and performance thresholds as implementation decisions with rationale and alternatives.
