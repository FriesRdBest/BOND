# BOND

## Engineering assurance, grounded in evidence

BOND connects service ownership, maturity rules, and warehouse telemetry
so an engineering finding can be understood, assigned, and eventually
resolved through a controlled improvement workflow.

The foundation is working. The complete journey from recommendation
through approval, simulated action, and independent verification is
under development.

[Explore the hosted demonstration](https://b-o-n-d.streamlit.app/)
· [Inspect the architecture](docs/ARCHITECTURE.md)
· [Review verified progress](docs/PHASE_ONE.md)
· [Read current limitations](docs/KNOWN_LIMITS.md)

BOND is an independent portfolio project. It is not an official Cortex
product and does not imply endorsement.

## The problem

A failing score alone does not tell an engineer what to do next.

Useful engineering assurance needs context: the affected service,
accountable owner, evidence source, applicable rule, and a clear way
to verify that an improvement actually worked.

BOND explores that connection. Its purpose is not to reproduce the
breadth of an engineering operations platform, but to demonstrate a
focused path from evidence to an accountable result.

## Explore the workspace

| Surface | What it explains |
| --- | --- |
| Scorecard Console | Organization maturity, evidence coverage, ownership gaps, and failing rules. |
| Catalog Repository | Service identity, dependencies, ownership, and the evidence behind individual rule results. |
| Pipeline Laboratory | A synthetic warehouse window with credit consumption, query samples, and explicit latency calculations. |
| Engineering Notes | Architecture, measurement boundaries, current mode, and implementation limits. |

## A short reviewer walkthrough

Open the Scorecard Console to see how passing, failing, and unknown
results contribute to organization maturity.

Open the Catalog Repository and inspect Billing Export. Its fixture
deliberately contains an ownership gap and a critical vulnerability,
making the relationship between evidence and score easy to inspect.

Inspect Policy Evaluator to see missing vulnerability evidence treated
as unknown rather than passing.

Open the Pipeline Laboratory to inspect the query samples behind the
latency summary. Credits are warehouse consumption units, not an
asserted monetary saving.

Finish with Engineering Notes and the linked source files to
distinguish implemented behavior from the remaining workflow.

## What works today

| Capability | Current state |
| --- | --- |
| Console navigation | Three primary consoles and a supporting technical view. |
| Catalog inspection | Search, ownership filtering, service detail, dependencies, and rule explanations. |
| Maturity evaluation | Three deterministic, equally weighted rules with missing evidence reported separately. |
| Warehouse demonstration | Fixed synthetic query samples, nearest rank P95, and Decimal credit rate calculations. |
| Shared backend services | Domain evaluation reused by the Streamlit interface and read only FastAPI endpoints. |
| PostgreSQL foundation | Versioned schema, migration checksums, synthetic catalog seed, and verified repository reads. |
| Application safety | The current interface and API use fixtures, not administrative database access. |
| Automated verification | Python formatting, lint, strict source type checking, domain tests, API tests, and Streamlit execution tests. |

## What is still being built

| Area | Remaining work |
| --- | --- |
| Interface refinement | Purposeful React and TypeScript evidence interaction, richer console context, and broader responsive review. |
| Assurance journey | Recommendations, authorized approval, simulated execution, and independent verification. |
| Durable workflow | Session isolation, persisted action state, and an inspectable event history connected to the interface. |
| Runtime security | Restricted database credentials, tested permissions, and application access policies. |
| Release verification | Browser accessibility checks, recovery tests, performance measurements, container validation, and hosted acceptance. |

The presence of a table, adapter, workflow file, or test tool is not
treated as proof that the corresponding product capability is complete.

## Architecture

```text
Streamlit workspace              FastAPI interface
         |                              |
         +---- Shared application ------+
                      |
            Typed domain contracts
            Deterministic rule logic
                      |
             Repository interfaces
                 /           \
        Fixture adapter   PostgreSQL adapter
```

Python owns application and domain logic. Pydantic validates contracts.
PostgreSQL provides the durable storage foundation. SQL migrations are
packaged with the application and checked against recorded SHA256 values.

React, TypeScript, and CSS are the selected tools for the next interface
phase. They are not presented as completed frontend implementation in
this foundation release.

The optional Snowflake integration boundary defaults to synthetic
evidence. Reviewers do not need warehouse credentials.

## Verification recorded

The foundation verification supplied on October 15, 2026 recorded:

| Check | Recorded result |
| --- | --- |
| Automated test suite | 57 passed. |
| Ruff | Passed. |
| Pyright | Zero errors and zero warnings. |
| Application dependency audit | No known vulnerabilities reported in the audited dependency set. |
| Local disclosure guard | Passed; its limited scope is documented. |
| Local Streamlit health | Passed on port 8501. |
| Local API health | Passed on port 8000. |
| PostgreSQL foundation | Initial migration, six synthetic services, adapter lookups, and migration replay verified. |

These are recorded local results, not a claim that every later commit
has passed. Inspect GitHub Actions for current workflow results.

The suite emitted one test client deprecation warning. That warning
remains recorded rather than suppressed.

Automated execution tests do not establish complete accessibility,
production capacity, or security certification.

## Run locally

Use Python 3.12 and uv. Install the locked environment, then start the
workspace from the repository root.

```bash
uv sync --locked
uv run streamlit run app.py
```

The fixture workspace does not require database credentials.

Start the separately runnable API in another terminal.

```bash
uv run uvicorn bond.api:app --host 0.0.0.0 --port 8000
```

Open `/docs` on the API service to inspect its read only contracts.

Run the current automated checks.

```bash
uv run ruff format --check src tests scripts app.py
uv run ruff check src tests scripts app.py
uv run pyright
uv run pytest -q
uv run python scripts/check_secrets.py
```

See [local development](docs/LOCAL_DEVELOPMENT.md) for additional
instructions and [persistence](docs/PERSISTENCE.md) for explicit database
operator commands. Operator credentials do not belong in the public
interface.

## Hosting and data boundaries

The submission uses Streamlit Community Cloud and Supabase free
allowances. Free services can sleep, pause, or impose limits.
Continuous availability is not promised.

Evidence in the current interface is synthetic and fixed in time.
Charts are not live warehouse observations. No production infrastructure
actions are performed.

Client database certificate and hostname verification passed in the
recorded operator check. The separate pooler to PostgreSQL link was not
reported as TLS. This distinction remains an open security review item;
BOND does not claim that every connection is encrypted.

## Engineering records

| Record | Contents |
| --- | --- |
| [Project charter](docs/PROJECT.md) | Purpose, scope, and product boundaries. |
| [Architecture](docs/ARCHITECTURE.md) | Layer responsibilities and integration boundaries. |
| [Design standards](docs/DESIGN.md) | Tokens, typography, motion, and accessibility expectations. |
| [Delivery plan](docs/DELIVERY.md) | Five phases and acceptance checks. |
| [Phase one evidence](docs/PHASE_ONE.md) | Recorded verification and outstanding work. |
| [Phase two contract](docs/PHASE_TWO.md) | Console refinement and component acceptance requirements. |
| [Security](docs/SECURITY.md) | Credential handling and verification expectations. |
| [Known limits](docs/KNOWN_LIMITS.md) | Incomplete capabilities and maintenance findings. |
| [Operating plan](docs/OPERATIONS.md) | Hosting, recovery expectations, and the ninety day plan. |
| [Decision register](docs/DECISIONS.md) | Decisions and their rationale. |

## Development transparency

BOND is being built with AI assistance for research, implementation,
documentation, and review. The applicant remains responsible for
understanding the system, validating its behavior, and explaining its
decisions.

## License

BOND is licensed under the [Apache License 2.0](LICENSE).
