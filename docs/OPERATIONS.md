# BOND operating plan

## Submission hosting

Streamlit Community Cloud hosts the application. Supabase PostgreSQL stores durable state. Target zero cost within free allowances. Do not promise continuous availability, unlimited capacity, or zero startup latency. No paid resource is authorized by this plan.

## Initial configuration

| Variable | Purpose |
| --- | --- |
| BOND_DB_HOST | Session pooler host. |
| BOND_DB_PORT | Database port. |
| BOND_DB_NAME | Database name. |
| BOND_DB_USER | Restricted runtime username after provisioning. |
| BOND_DB_PASSWORD | Private database password. |

The owner reported saving these names in Codespaces. Their values and authentication have not been verified. Configure deployed Streamlit secrets separately. Require encrypted database transport in the implementation and verify the selected driver settings.

## Recovery requirements

Define and test recovery for connection interruption, failed migration, duplicate action requests, stale evidence, and demo reset. Do not claim backup or restoration capability without configuring and exercising it. Record recovery steps and observed results during hardening.

## Days 1 to 30

Validate the deployed reviewer journey, examine errors, review database permissions, measure actual resource use, and maintain a documented inventory of limits. Establish tested export and restoration procedures appropriate to the selected hosting tier.

## Days 31 to 60

Review query plans, indexes, evidence freshness, rule quality, session isolation, dependency updates, and accessibility findings. Improve only where measurements or reviewer feedback justify changes.

## Days 61 to 90

Assess whether demand justifies independent API hosting, workers, scheduled ingestion, stronger tenancy, or paid infrastructure. Record costs and alternatives before changes. Rehearse migration and rollback in a suitable environment before claiming readiness.
