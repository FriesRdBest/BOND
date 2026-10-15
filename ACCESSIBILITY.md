# Accessibility

BOND should be usable by people using keyboards, screen readers, magnification, reduced motion settings, and different viewport sizes.

This document explains BOND’s accessibility priorities, contributor expectations, reporting process, and current limitations. It does not claim conformance with a particular accessibility standard.

## Priorities

BOND prioritizes these outcomes:

- Keyboard users can reach and operate the primary workflow.
- Focus remains visible while moving through interactive controls.
- Important status changes are announced through appropriate live regions.
- Color is not the only way to understand passing, warning, failing, or unknown states.
- Text and controls remain readable at common zoom levels.
- Layouts avoid horizontal overflow on narrower viewports.
- Nonessential motion respects a user’s reduced motion preference.
- Evidence, recommendations, approvals, simulated actions, and verification outcomes use clear labels rather than relying on visual position alone.

These are product priorities and areas of active verification. They are not a claim that every possible accessibility barrier has been found or resolved.

## Contributor expectations

Contributions that affect a user facing interface should preserve accessible structure and behavior.

Before opening a pull request, contributors should consider:

- Whether every interactive control has an accessible name.
- Whether keyboard focus can reach and operate the control.
- Whether focus remains visible.
- Whether status is communicated by text or an appropriate live region, not color alone.
- Whether images and visual indicators have useful text alternatives where needed.
- Whether the layout remains usable at narrower viewports and higher zoom levels.
- Whether animation is necessary and respects reduced motion preferences.

The evidence explorer uses semantic landmarks, labeled controls, visible focus styles, status regions, and reduced motion handling. Frontend contract tests and browser tests cover selected interaction and rendering behavior.

Automated checks help catch regressions, but they do not prove that an interface is accessible to every person or assistive technology. Contributors should describe the accessibility evidence included with a user facing change.

## Reporting accessibility issues

If you encounter a barrier, open an issue using the [Accessibility report template](https://github.com/FriesRdBest/BOND/issues/new?template=accessibility_report.yml).

Useful information includes:

- The page, console, or workflow affected.
- What you expected to happen.
- What happened instead.
- The steps needed to reproduce the barrier.
- Your browser, operating system, zoom level, viewport size, and assistive technology when relevant.

Screenshots or recordings are optional. You do not need to disclose a disability to report a barrier.

Do not include passwords, tokens, database credentials, or other private information in an issue.

## Severity

Reporters may describe impact, but maintainers confirm severity during review.

| Impact | Practical meaning |
| --- | --- |
| Blocker | A core workflow cannot be completed. |
| Major | A workflow is difficult or unreliable. |
| Moderate | Some information or control is harder to use. |
| Minor | The experience can be improved. |

## How we respond

Accessibility reports are triaged with other repository issues. A report may receive a request for more detail, a workaround, a fix, or an explanation of why the current behavior is intentional.

BOND is an independent portfolio project maintained by one developer. Response times depend on availability and cannot be guaranteed. Reports remain visible in the issue tracker so their status and resolution can be inspected.

## Ownership and maintenance

The repository owner is responsible for reviewing accessibility reports, maintaining the accessibility documentation, and deciding which fixes enter the product roadmap.

Accessibility is considered during interface changes, automated testing, and release review. Ownership remains with the repository owner unless a future contributor arrangement is documented.

## Supported environments

The hosted demonstration is intended to work in current versions of major desktop and mobile browsers.

The evidence explorer has been exercised with automated browser tests covering rendering, keyboard selection, the Python inspection bridge, native fallback, visible label pointer activation, narrow catalog containment, scoped component accessibility, and query filtering.

This does not establish support for every browser, device, screen reader, input method, or assistive technology combination.

## Known limitations

BOND does not claim complete accessibility conformance. Automated tests and source inspection do not replace evaluation with assistive technology users.

The public demonstration uses synthetic evidence and simulated actions. Its hosted availability depends on free Streamlit Community Cloud and Supabase allowances, which may sleep, pause, restart, or impose resource limits.

Known limitations and incomplete capabilities are maintained in [KNOWN_LIMITS.md](docs/KNOWN_LIMITS.md). Accessibility barriers should be reported through the Accessibility report template so they can be tracked and addressed.

## Feedback and improvements

Suggestions for improving this statement or BOND’s accessibility practices can be opened as a feature request.

Active barriers should be reported through the [Accessibility report template](https://github.com/FriesRdBest/BOND/issues/new?template=accessibility_report.yml).
