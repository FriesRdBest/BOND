# BOND project charter

## Purpose

BOND connects service ownership, engineering evidence, maturity rules, and Snowflake telemetry to an approved improvement with a recorded verification result. It demonstrates engineering judgment through a complete workflow rather than a broad imitation of Cortex.

## Core journey

Ingest evidence, evaluate a versioned rule, identify an accountable owner, explain a recommendation, obtain authorized approval, perform a clearly simulated action, verify the result, and preserve an audit history. An attempted action is not a verified success.

## Product surfaces

| Surface | Responsibility |
| --- | --- |
| Scorecard Console | Organization maturity, compliance drift, rule results, ownership coverage, and evidence inspection. |
| Catalog Repository | Service identity, ownership, dependencies, API contract evidence, vulnerability evidence, and improvement history. |
| Pipeline Laboratory | Ingestion freshness, warehouse credits, query latency, application connection pool telemetry, and recommendation state. |

Evidence detail, approval review, verification, audit history, and technical explanation support these consoles. Exact secondary navigation labels remain subject to implementation.

## Boundaries

BOND is not an official Cortex product, a replacement for Cortex, or a production infrastructure control plane. Public actions use synthetic data and simulation. Real integrations require explicit configuration and permission. No Snowflake account is required to explore the submission.

## Submission

Provide a live Streamlit application and a public GitHub repository with clear links between them. Reviewers need no database credentials. Explain the product, architecture, limitations, demo instructions, and measured results. Disclose material AI assistance and retain human accountability.

## Hosting and portability

Target zero hosting cost within Streamlit and Supabase free allowances. No paid resource or custom domain is required. Free services can sleep, pause, or impose limits. Do not promise continuous availability. Keep business logic and storage boundaries portable. A future standalone React website requires interface integration work, not merely a hosting switch.

## Research honesty

Prior research covered selected Cortex website pages, the role, culture memo, documentation entry points, public repository listings, and CLI configuration. It was not an exhaustive audit of every page or implementation. Do not claim otherwise.

## Starting state

At the initial setup audit, main contained README.md, LICENSE, and .gitignore. Their presence was verified, not their complete content. Supabase reported ACTIVE_HEALTHY with PostgreSQL 17 in us-west-2. Its security advisor returned no notices. Connection authentication, API exposure settings, application permissions, and deployed behavior were not verified. The owner reported creating Codespaces secrets and opening a fresh terminal on main. Streamlit deployment remains pending.

## Open implementation decisions

Choose and record dependency versions, directory structure, full token map, font family, relational schema, application roles, session isolation mechanism, rule weights, API contracts, and performance thresholds during implementation. Do not present these as completed.
