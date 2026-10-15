# Contributing to BOND

Thank you for considering a contribution to BOND.

BOND is an independent engineering assurance workbench. It connects service ownership, maturity rules, warehouse telemetry, and a controlled improvement workflow. Contributions should preserve its clear product boundaries, honest evidence, and reviewable engineering standard.

## Before contributing

Read the [project charter](docs/PROJECT.md), [architecture record](docs/ARCHITECTURE.md), [security notes](docs/SECURITY.md), and [known limits](docs/KNOWN_LIMITS.md).

Please open an issue before submitting a substantial change. This helps clarify the intended behavior, scope, and verification approach before implementation begins.

## Ways to contribute

| Contribution | Useful focus |
| --- | --- |
| Bug report | A reproducible failure, expected result, actual result, and relevant environment details. |
| Documentation improvement | A clearer explanation, corrected instruction, or more precise boundary. |
| Interface improvement | Accessibility, readability, responsive behavior, or interaction clarity. |
| Backend improvement | Domain correctness, persistence behavior, authorization, recovery, or test coverage. |
| Security concern | A private report through the process in [SECURITY.md](SECURITY.md). |

## Development workflow

1. Fork the repository or create a focused branch from `main`.
2. Install the locked development environment with `uv sync --locked`.
3. Make a focused change with a clear purpose.
4. Add or update tests for behavior that can be verified automatically.
5. Run the local quality gates.
6. Open a pull request with a concise explanation of the change and evidence.

## Local quality gates

Run these commands from the repository root.

```bash
uv run ruff format --check src tests scripts app.py
uv run ruff check src tests scripts app.py
uv run pyright
uv run pytest -q
uv run python scripts/check_secrets.py
```

For frontend changes, also run the checks in `frontend/evidence`.

```bash
cd frontend/evidence
npm ci --ignore-scripts
npm run build
npm test
```

A pull request should pass the repository’s automated checks. If a check cannot run in the available environment, explain that limitation clearly in the pull request.

## Commit and pull request expectations

Use a concise commit title that describes the change. Use the commit body to explain the reason, important decisions, and verification actually performed.

Do not include secrets, credentials, generated artifacts, unrelated formatting changes, or unsupported claims. Do not describe planned work as implemented behavior.

## Product boundaries

BOND uses synthetic evidence by default and performs simulated actions in its public demonstration. Contributions must not imply official affiliation with Cortex, claim production control over external systems, or present synthetic results as live warehouse observations.

## License

By contributing, you agree that your contributions are licensed under the [Apache License 2.0](LICENSE).
