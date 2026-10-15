# Persistence foundation

## Database boundaries

The bond schema contains the synthetic catalog, demo session identities, and
an initial audit event table. The bond_meta schema contains migration history.
Neither schema is intended for public Data API exposure.

The catalog stores validated service documents as JSONB with a relational
primary key. This supports the initial typed contract without inventing a
complete operational schema before the workflow is implemented.

Approval state, evidence history, and verification results require subsequent
migrations. The initial audit table is infrastructure, not a completed audit
workflow.

## Migration discipline

Packaged SQL files are applied in filename order. A transaction advisory lock
serializes cooperating migration runners. Each applied file has a recorded
SHA256 checksum. Changed or unknown migration history blocks execution.

Do not edit an applied migration. Add a new migration instead.

The migration transaction has lock and statement timeouts. The operator script
prints controlled status messages without raw connection errors.

## Initial access posture

Row security is enabled on the three application tables. No application access
policies are introduced in the first migration. Public schema privileges and
the named Supabase API roles are explicitly revoked for the application schema.

The initial operator uses setup credentials. Successful operator reads do not
prove runtime isolation because privileged owners can bypass ordinary row
security. A restricted runtime role, application permissions, and public demo
session enforcement remain required before deployment.

## Synthetic catalog

The explicit seed command writes only the six packaged synthetic services.
It does not create visitor sessions or audit history. Existing identical
documents are not rewritten. The command is not an application startup action.

## Connection lifecycle

The initial adapter opens a connection for each repository operation. This
prioritizes clear transaction ownership during the foundation stage. It is not
a claim of optimized connection pooling. Pooling and pool telemetry require
implementation and measurement later.

## Operator commands

Run these from the repository root using the project environment.

```bash
uv run python scripts/database.py --plan
uv run python scripts/database.py --apply
uv run python scripts/database.py --seed
uv run python scripts/database.py --verify
```

The plan and verify commands are read only. Apply changes schema and migration
history. Seed changes synthetic catalog data. Do not execute operator commands
from the public interface.

## Outstanding transport observation

The client connection passed certificate and hostname verification. The
database view did not report TLS for the separate pooler to PostgreSQL link.
Retain this distinction in the security review. Do not claim every connection
uses TLS.
