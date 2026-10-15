# BOND contributor instructions

Read docs/PROJECT.md, docs/DELIVERY.md, docs/ARCHITECTURE.md, docs/DESIGN.md, and docs/SECURITY.md before changing the application.

BOND is an independent engineering assurance workbench built for a portfolio submission. It is not an official Cortex product. Do not imply endorsement, existing customers, production history, or completed capabilities without evidence.

The hosted application uses Streamlit Community Cloud and Supabase PostgreSQL within free allowances. Python owns domain logic. Pydantic owns typed validation. React, TypeScript, and CSS may supply purposeful custom components. FastAPI remains a separately runnable backend interface. Do not add languages merely to resemble another organization.

Keep domain logic independent of Streamlit, FastAPI, database clients, and external integrations. Use repository interfaces. Use immutable domain values where appropriate. Default to reproducible synthetic evidence and simulated actions. Preserve provenance and distinguish missing evidence from passing evidence.

Inspect existing files before replacing them. Work directly on main during initial construction as requested by the owner. Before submission, enable required checks and branch protection. External writes and paid resources require the applicable explicit approval. Never infer that a connector is available without checking.

Never print, commit, or copy secrets into documentation. Test secret presence without showing values. Never use administrative database credentials for routine deployed operations. Do not claim a connection works until a safe authentication test succeeds.

Human facing prose uses headings, short paragraphs, and tables. Avoid dot point lists and hyphenated words in authored prose. Preserve required technical syntax, URLs, identifiers, standard names, and license text. Use calm, respectful language without inflated claims.

Use manageable, complete terminal batches. Do not overwrite unrelated work. Commit titles describe the actual change. Extended commit bodies explain why, important decisions, and checks actually run. Never fabricate passing results, team activity, or history.

Run applicable formatting, type, test, security, and accessibility checks as they become available. Report checks not run and why. A planned tool is not an executed check. Update documentation when decisions or verified status change.
