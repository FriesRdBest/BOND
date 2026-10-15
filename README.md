# BOND

## Engineering assurance, grounded in evidence

BOND connects service ownership, maturity rules, and warehouse telemetry
so an engineering finding can be understood, assigned, approved, acted on
in a clearly simulated demonstration, verified, and preserved in an
inspectable audit history.

The hosted demonstration implements the complete evidence to verification
journey. Recommendations are isolated by demonstration session, workflow
requests use idempotency identifiers, and execution is explicitly simulated.

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
| Catalog Repository | Service identity, dependencies, ownership, evidence, recommendations, workflow state, and audit history. |
| Pipeline Laboratory | A synthetic warehouse window with credit consumption, query samples, and explicit latency calculations. |
| Engineering Notes | Architecture, measurement boundaries, current mode, and implementation limits. |

## A short reviewer walkthrough

Open the Scorecard Console to see how passing, failing, and unknown
results contribute to organization maturity.

Open the Catalog Repository and inspect Billing Export. Its fixture
deliberately contains an ownership gap and a critical vulnerability,
making the relationship between evidence and score easy to inspect.

In the native service inspection area, propose a recommendation from the
`ownership_assigned` finding. Approve it, record the simulated execution,
and verify the outcome. Expand **Audit history** to inspect the recorded
recommendation, approval, simulated action, and verification events.

Inspect Policy Evaluator to see missing vulnerability evidence treated
as unknown rather than passing.

Open the Pipeline Laboratory to inspect the query samples behind the
latency summary. Credits are warehouse consumption units, not an
asserted monetary saving.

Finish with Engineering Notes and the linked source files to
distinguish implemented behavior from the remaining hardening and
release work.

## What works today

| Capability | Current state |
| --- | --- |
| Console navigation | Three primary consoles and a supporting technical view. |
| Catalog inspection | Search, ownership and result filters, React evidence exploration, native fallback, dependencies, and rule explanations. |
| Maturity evaluation | Three deterministic, equally weighted rules with missing evidence reported separately. |
| Assurance workflow | Recommendation proposal, approval or rejection, simulated execution, independent verification, idempotent requests, session isolation, and audit history. |
| Workflow interfaces | Streamlit workflow controls and separately runnable FastAPI endpoints for the workflow journey. |
| Atomic persistence | Workflow events and recommendation state changes commit together or roll back together in the memory and PostgreSQL adapters. |
| Workflow recovery | Failed proposals and transitions roll back, repeated requests do not duplicate an operation, and request identifiers cannot be reused for a different operation. |
| Concurrent transition safety | A transition rechecks recommendation state after acquiring the session transaction lock, preventing an approval from overwriting a competing rejection. |
| Warehouse demonstration | Fixed synthetic query samples, nearest rank P95, and Decimal credit rate calculations. |
| PostgreSQL foundation | Versioned schema, migration checksums, synthetic catalog seed, workflow migrations, session scoped row level security, and a restricted application role. |
| Application safety | The public interface uses fixtures and an in memory demonstration store by default; it does not use administrative database access. |
| Automated verification | Python formatting, lint, strict source type checking, domain tests, API tests, Streamlit execution tests, frontend contract tests, and real browser tests. |

## What remains for release

| Area | Remaining work |
| --- | --- |
| Interface acceptance | Final owner visual review, broader responsive inspection, and hosted acceptance of the implemented interface. |
| Durable public workflow | Decide and verify whether the hosted public demonstration should connect to PostgreSQL rather than remain in memory mode by default. |
| Database hardening | Review migration table access, add covering indexes for workflow event foreign keys, and optimize row level security policy evaluation. |
| Release verification | Hosted acceptance and final submission safeguards. |
| Submission safeguards | Final repository review, main protection, and required checks. |

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

React, TypeScript, and CSS implement the evidence explorer through Streamlit
V2. Its production assets ship inside the Python package, with source and
output checksums. The hosted interface requires no separate frontend server.

The optional Snowflake integration boundary defaults to synthetic
evidence. Reviewers do not need warehouse credentials.

## Verification recorded

The latest verified checkpoint is `2ac9cb3`, “Record October 15 technical
verification.” At that checkpoint, the local quality gates, live Supabase
authorization and atomic persistence checks, frontend contract tests, browser
tests, dependency audits, and Docker image build completed successfully.

| Check | Recorded result |
| --- | --- |
| Python test suite | 113 passed. |
| PostgreSQL atomic, authorization, and persistence tests | 16 passed. |
| Frontend contract tests | 6 passed. |
| Explorer bridge, contract, event, and query navigation tests | 24 passed. |
| Ruff format and lint | Passed. |
| Pyright | Zero errors and zero warnings. |
| Dependency audits | Zero vulnerabilities reported in the inspected application and frontend dependency sets. |
| Live database authentication | Passed with client certificate and hostname verification. |
| Restricted runtime role | Application isolation, row level security isolation, cross session insertion denial, metadata access denial, and audit mutation privilege denial were verified. |
| Atomic persistence | Proposal and transition operations commit their event and state change together or roll back together. |
| Concurrent transition safety | A competing rejection prevents a later approval from using stale state. |
| Docker image build | Passed; image digest `sha256:347d1c9b0aafea683db76387734ebc89ee842fa38421a4bab4ebdf378f775695`. |
| GitHub Quality workflow | Python contracts, frontend build, browser behavior, and dependency checks passed. |
| GitHub CodeQL workflow | Python and JavaScript TypeScript analysis passed. |

These results describe the verified checkpoint, not a claim that every
future commit has passed. Inspect GitHub Actions for current workflow
results.

The Python suite emits one test client deprecation warning. That warning
remains recorded rather than suppressed.

Automated execution tests do not establish complete accessibility,
production capacity, security certification, live database recovery, or
unrestricted hosted availability.

See [the October 15 verification record](docs/VERIFICATION_2026-10-15.md)
for the complete scope, results, and boundaries.

## Assurance workflow

The Catalog Repository connects evidence findings to a controlled
improvement workflow. A reviewer can propose a recommendation from failing or
missing evidence, approve or reject it, record a simulated execution, verify
the outcome, and inspect its audit history.

Workflow requests use request identifiers for idempotency. Recommendations
and events are isolated by demonstration session. Execution is explicitly
simulated and does not change production infrastructure.

A proposal must use the rule version represented by the evaluated evidence.
A workflow event and its resulting recommendation state are saved in one
atomic transaction. If that transaction fails, neither the event nor the
state change remains.

The public interface uses an in memory demonstration store by default. The
PostgreSQL workflow repository, migrations, restricted role, and session
scoped row level security are implemented. Hosted PostgreSQL mode remains
separate work until its live connection, rollback behavior, and session
isolation are verified.

See [the phase three scope record](docs/PHASE_THREE.md),
[the phase three verification record](docs/PHASE_THREE_VERIFICATION.md),
and [the phase four verification record](docs/PHASE_FOUR_VERIFICATION.md).

## Earlier phase evidence

The phase two run passed 86 Python tests, six frontend contract
tests, and six real Chromium browser tests. Python and frontend source type
checks and lint passed.

Browser checks exercised actual rendering, keyboard selection, the Python
inspection bridge, native fallback, visible label pointer activation, narrow
catalog containment, scoped component accessibility, and query filtering.

A clean frontend installation with dependency lifecycle scripts disabled
rebuilt successfully. The frontend audit reported zero vulnerabilities.
The hashed application dependency audit reported no known vulnerabilities.

Wheel verification confirmed registration metadata, required assets, output
checksums, and current source provenance.

These are recorded local results. The updated GitHub jobs, owner visual
approval, and hosted acceptance are separate gates.

See [the phase two verification record](docs/PHASE_TWO_VERIFICATION.md)
for scope and remaining limitations.

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

Open `/docs` on the API service to inspect its contracts.

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
| [Phase three scope](docs/PHASE_THREE.md) | Assurance workflow scope and boundaries. |
| [Phase three verification](docs/PHASE_THREE_VERIFICATION.md) | Recorded phase three checks and limitations. |
| [Phase four verification](docs/PHASE_FOUR_VERIFICATION.md) | Restricted authorization, atomic persistence, and recovery evidence. |
| [October 15 verification](docs/VERIFICATION_2026-10-15.md) | Current technical verification results and boundaries. |
| [Security](docs/SECURITY.md) | Credential handling and verification expectations. |
| [Known limits](docs/KNOWN_LIMITS.md) | Incomplete capabilities and maintenance findings. |
| [Operating plan](docs/OPERATIONS.md) | Hosting, recovery expectations, and the ninety day plan. |
| [Decision register](docs/DECISIONS.md) | Decisions and their rationale. |

## Development transparency

BOND is being built with AI assistance for research, implementation,
documentation, and review. I remain responsible for understanding the
system, validating its behavior, and explaining its decisions.

## License

BOND is licensed under the [Apache License 2.0](LICENSE).
