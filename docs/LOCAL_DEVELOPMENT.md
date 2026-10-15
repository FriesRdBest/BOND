# Local development

## Runtime

Use Python 3.12 and the committed uv.lock. The fixture application does not
require database credentials. The current Codespace has uv installed in
the owner tooling environment. Future configured containers install uv directly.

## Install and check

```bash
uv sync --locked
uv run ruff format --check src tests scripts app.py
uv run ruff check src tests scripts app.py
uv run pyright
uv run pytest -q
uv run python scripts/check_secrets.py
```

## Run the interface

```bash
uv run streamlit run app.py
```

The workspace runs on port 8501. Keep Codespaces port access private during
development unless explicitly choosing to share it.

## Run the API

```bash
uv run uvicorn bond.api:app --host 0.0.0.0 --port 8000
```

Interactive API documentation is available at /docs on the API service.
The initial endpoints expose only synthetic read only evidence. They do not
prove a completed authorization or action workflow.

## Database operator

Use scripts/database.py only through the explicit operator commands recorded
in docs/PERSISTENCE.md. Do not use operator credentials in the public interface.

## Dependency records

uv.lock is the dependency authority. requirements.txt is a deployment export
including the local package. Regenerate it when dependencies change.

```bash
uv export --locked --no-dev --no-hashes --format requirements-txt --output-file requirements.txt
```

## Container

```bash
docker build -t bond .
docker run --rm -p 8501:8501 bond
```

Container instructions require an actual build test before being described
as verified. The initial base image uses a version tag; pin its reviewed digest
before the submission release.

## Automated checks

Streamlit AppTest exercises page execution and an empty search state without
a browser. It does not verify rendered contrast, responsive behavior, focus,
screen reader output, or animation. Manual and browser based review remain.

GitHub workflow actions are resolved to full revisions during setup.
Their presence does not mean a workflow has run. Inspect actual Actions
results after the code is pushed.
