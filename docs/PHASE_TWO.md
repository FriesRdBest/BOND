# Phase two interface contract

## Objective

Refine the three consoles into a coherent evidence inspection workspace
while preserving the verified domain and persistence foundation.

## Selected integration

Use the supported Streamlit V2 component interface for a React and
TypeScript evidence explorer. Confirm installed package compatibility
before selecting dependencies. Keep compiled assets inside the Python
package so hosted operation requires no separate frontend server.

The component must add useful service and rule evidence interaction,
not decoration. Treat component messages as untrusted input and validate
them in Python. Retain a native service inspection path.

V2 style isolation is not a security sandbox. Never send credentials
into component data or render untrusted content as executable markup.

## Shared design

The existing design token file remains the source of truth. Preserve
the recorded canvas, surfaces, typography, status colors, focus
treatment, spacing, and reduced motion behavior. Do not introduce a
second independent palette.

## Scope

| Surface | Required refinement |
| --- | --- |
| Scorecard Console | Score explanation, attention queue, and navigation to affected services. |
| Catalog Repository | Search, ownership and status filters, dependency context, and evidence exploration. |
| Pipeline Laboratory | Clear warehouse context, query inspection, units, and fixed observation labels. |
| Engineering Notes | Concise architecture, measurement methods, limits, and source access. |

## Acceptance

| Check | Status |
| --- | --- |
| Existing foundation tests remain passing | Passed in the 86 test suite |
| Python formatting, lint, and strict types | Passed |
| Frontend strict types, lint, tests, and production build | Passed |
| Component messages validated against known services | Passed contract and browser checks |
| Production assets included in the Python package | Passed with metadata and provenance checks |
| Native inspection fallback works | Passed keyboard and pointer checks |
| Browser keyboard and automated accessibility checks | Passed for the documented component scope |
| Desktop and narrow viewport containment | Catalog browser check passed; broader visual review pending |
| GitHub workflow results inspected | Pending |
| Owner visual review at the end of the phase | Pending |

## Working method

Use complete terminal batches in the existing Codespace. Run automated
checks during construction. Do not require manual file replacement.
Defer visual review until implementation of the phase is complete.

## Boundaries

Approval execution, public session isolation, restricted runtime access,
recovery, and production capacity remain later work. Retain the current
maintenance warning and upstream transport observation until a reviewed
change resolves them. Do not add artificial loading delays or claim
fixed fixtures are live telemetry.
