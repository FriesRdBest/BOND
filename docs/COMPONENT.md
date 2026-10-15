# Evidence explorer component

## Purpose

The React and TypeScript explorer provides service selection and rule evidence
inspection. It is not a second application or a production control surface.
An explicit inspection event can request a known service in the Python catalog.

## Integration

Use the Streamlit V2 renderer interface. The frontend receives a validated
payload, mounts into the supplied component element, and returns cleanup.
Style isolation is not a security sandbox.

The first component batch builds assets and contracts. Console mounting and
browser verification follow in subsequent batches.

## Contracts

Python validates the payload and browser messages with Pydantic. TypeScript
validates incoming data with Zod. Inspection messages carry a schema version,
an explicit action, a known service identifier, and a request UUID.

A valid UUID is not authentication. Selection validation does not authorize
infrastructure actions. No such actions exist in this component.

## Tokens

The build reads the existing design token source and generates primitive,
semantic, and component variables. The component does not own a separate
palette. Reduced motion and visible keyboard focus are required.

## Build and deployment

Frontend source lives under frontend/evidence. npm records exact resolved
direct dependencies and a package lock. The build packages production assets
under src/bond/data/web/evidence.

The Python application ships those assets. Hosted Streamlit does not need a
Node process or a separate frontend development server. Rebuild assets when
the frontend source, package lock, or shared tokens change.

The manifest records source and output checksums. Packaging verification checks
that required assets and their recorded output hashes are present in the wheel.

## Type scope

TypeScript source uses strict checking. skipLibCheck skips dependency
declaration checking, not application source checking. This is not a claim
that external library declarations have been independently verified.

TypeScript 5.9 is selected because the inspected TypeScript ESLint release
does not support TypeScript 7. Do not upgrade one tool independently without
checking the compatibility constraints.

## Remaining acceptance

Forwarding and contract tests do not prove accessibility. Browser tests,
native fallback checks, narrow viewport checks, and actual Streamlit component
interaction must pass before this component is considered integrated.

## Packaged registration

The component declaration is stored in src/bond/pyproject.toml. Its project name matches the installed distribution. The registered component name is bond.evidence_explorer, and asset_dir is data/web/evidence relative to that metadata file.

The bridge references evidence.js and evidence.css as packaged assets. The asset directory is publicly served and must contain only intended browser assets, public license material, and build provenance. Never place credentials or private data in this directory.

## AppTest component discovery compatibility

Streamlit issue 15484 documents an AppTest runtime that does not discover installed packaged components before rendering. This can produce the same missing asset declaration exception even when component metadata and assets exist.

The affected AppTest modules initialize the real component manager with discover_and_register_components and file watching disabled. No component implementation or return value is mocked. No failing test is skipped and no installed library file is modified.

This is a version sensitive test harness compatibility adjustment. Reassess it when upgrading Streamlit. It does not replace browser verification against the normal application runtime.

Upstream reference:

https://github.com/streamlit/streamlit/issues/15484

## Distribution identity and editable discovery

The original distribution name was bond-assurance while the import package
was bond. The inspected Streamlit scanner normalizes distribution names by
replacing hyphens with underscores and uses that name for import discovery.

For the editable installation this produced bond_assurance, which did not
identify the existing bond package. Finding the manifest inside the source
tree was therefore not enough to establish installed component discovery.

The distribution name is now bond, matching the existing import package.
The product and repository remain BOND. The qualified component name is
bond.evidence_explorer.

A regression test invokes the real installed scanner and verifies the
resolved component asset directory. Keep the actual discovery test alongside
the structural metadata test and the AppTest runtime initialization.

## Reviewer entry links

The view query parameter selects the initial workspace page. Supported values are scorecard, catalog, pipeline, and engineering. Unknown values fall back to the Scorecard Console. Existing session navigation takes precedence after initialization.

This is navigation, not authorization. No database credentials or infrastructure action parameters are accepted through these links.

## Browser verification scope

Playwright starts a separate local Streamlit runtime on port 8511. It verifies actual component rendering, keyboard selection, the inspection event bridge, native fallback, and narrow viewport containment. A scoped axe scan inspects the evidence component inside its shadow root.

The accessibility scan is limited to the rendered component and selected automated rules. It is not a complete application accessibility certification. Browser tests do not replace the owner visual review at the end of the phase.

## Transient inspection event handoff

Browser diagnosis observed a component callback while the later component result exposed no selection value. The bridge now reads the callback session state, validates it against the previously supplied view, and queues only the normalized inspection message.

The main render checks that message against the current view before consuming it. A request UUID prevents duplicate consumption within the current interface session. The accepted selection is included in the next component payload and returned to the native inspector.

This is interface event handling, not durable action execution, authentication, or authorization for infrastructure changes.

Browser verification checks the native combobox value rather than its container text, because the displayed selection is an input property.

## Current selection synchronization contract

The component now uses persistent selection state rather than a transient trigger. The selected service is interface state, not an infrastructure command.

The callback validates the message against the previously supplied service view and updates the canonical native selection before the main render. The main render retains current view validation and duplicate request protection.

This supersedes reliance on the earlier transient trigger handoff. A passing unit buffer test did not prove browser synchronization; the actual browser selection test remains the acceptance gate.
