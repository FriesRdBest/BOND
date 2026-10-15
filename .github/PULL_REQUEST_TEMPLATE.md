# Pull request

## Summary

Describe the change and the problem it addresses.

## Changes

- List the focused changes included in this pull request.

## Verification

Describe the checks you ran and their results.

```text
uv run ruff format --check src tests scripts app.py
uv run ruff check src tests scripts app.py
uv run pyright
uv run pytest -q
```

For frontend changes:

```text
cd frontend/evidence
npm ci --ignore-scripts
npm run build
npm test
```

## Boundaries

Confirm that this pull request does not introduce secrets, credentials, generated artifacts, unsupported claims, or changes to production infrastructure.

## Related issue

Link the related issue, if applicable.
