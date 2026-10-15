# Reviewer walkthrough

This walkthrough is intended for a technical reviewer evaluating BOND in
approximately 10 to 15 minutes. It distinguishes implemented behavior,
simulated demonstration behavior, and work that remains outside the current
submission.

BOND is an independent portfolio project. It is not an official Cortex product
and does not imply endorsement.

## What BOND demonstrates

BOND connects service ownership, maturity rules, warehouse telemetry, and a
controlled improvement workflow. A reviewer can inspect an evidence finding,
propose a recommendation, approve or reject it, record a simulated execution,
verify the outcome, and inspect the resulting audit history.

The interface uses fixed synthetic evidence. Execution is explicitly simulated
and does not change production infrastructure.

## Hosted walkthrough

Open the hosted demonstration:

<https://b-o-n-d.streamlit.app/>

1. **Scorecard Console.** Review organization maturity, evidence coverage,
   ownership gaps, and failing rules. Missing evidence is reported separately
   and does not count as passing.

2. **Catalog Repository.** Inspect **Billing Export**. The fixture intentionally
   includes an ownership gap and a critical vulnerability so the relationship
   between evidence and score is easy to follow.

3. **Improvement workflow.** In the native service inspection area, propose a
   recommendation from the `ownership_assigned` finding. Approve it, record the
   simulated execution, verify the result, and expand **Audit history**.

4. **Policy Evaluator.** Confirm that missing vulnerability evidence is treated
   as unknown rather than passing.

5. **Pipeline Laboratory.** Inspect the fixed query samples behind the latency
   summary. Warehouse credits are consumption units, not an asserted monetary
   saving.

6. **Engineering Notes.** Review the architecture, current operating mode,
   measurement boundaries, and implementation limits.

Workflow recommendations are isolated by demonstration session. A page refresh
begins a new session and does not expose another session’s workflow state.

## Local walkthrough

The repository uses Python 3.12 and `uv`.

```bash
git clone https://github.com/FriesRdBest/BOND.git
cd BOND
uv sync --locked
uv run streamlit run app.py
```

The default workspace uses packaged synthetic evidence and does not require
database credentials.

To inspect the API contracts:

```bash
uv run uvicorn bond.api:app --host 0.0.0.0 --port 8000
```

Then open <http://localhost:8000/docs>.

## Run the verification gates

```bash
uv run ruff format --check src tests scripts app.py
uv run ruff check src tests scripts app.py
uv run pyright
uv run pytest -q
uv run python scripts/check_secrets.py

cd frontend/evidence
npm ci
npm run test:browser
```

At the current verified checkpoint, the Python suite passes 120 tests, Ruff and
Pyright are clean, and all seven Playwright browser tests pass.

## Architecture in one minute

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
PostgreSQL provides durable workflow storage when restricted runtime settings
are supplied. The React evidence explorer is packaged inside the Python
application; no separate frontend server is required.

## Data and security boundaries

- Evidence in the public interface is synthetic and fixed in time.
- Workflow execution is simulated; no production infrastructure is changed.
- The public interface does not use administrative database credentials.
- PostgreSQL mode is selected only when restricted `BOND_DB_HOST`,
  `BOND_DB_USER`, and `BOND_DB_PASSWORD` settings are supplied.
- Without those settings, the application uses an in-memory demonstration
  store.
- The recorded client database connection used certificate and hostname
  verification. The separate pooler-to-PostgreSQL transport was not reported as
  TLS and remains an open security review item.

## Where to inspect evidence

| Topic | Record |
| --- | --- |
| Architecture | [Architecture](ARCHITECTURE.md) |
| Current verification | [October 15 verification](VERIFICATION_2026-10-15.md) |
| Security boundaries | [Security](SECURITY.md) |
| Persistence and operators | [Persistence](PERSISTENCE.md) |
| Known limitations | [Known limits](KNOWN_LIMITS.md) |
| Operations and recovery | [Operations](OPERATIONS.md) |
| Decisions | [Decision register](DECISIONS.md) |

## What this demonstration does not establish

BOND does not establish production capacity, continuous hosted availability,
complete accessibility conformance, security certification, live database
recovery, or unrestricted production readiness. Free Streamlit and Supabase
allowances may sleep, pause, or impose resource limits.
