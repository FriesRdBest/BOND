# Phase three: complete assurance journey

## Implemented workflow

BOND now connects evaluated evidence to a controlled improvement workflow.
A recommendation can be created only from failing or missing evidence for a
known synthetic service.

A recommendation moves through proposed, approved, simulated execution, and
verification states. Rejection is available before approval. A failed
verification moves the recommendation to review required rather than claiming
success.

Every accepted transition records a distinct audit event. A repeated request
identifier returns the existing recommendation without creating a duplicate
event. Recommendations and events are isolated by demonstration session.

## Interface journey

The Catalog Repository exposes the workflow beside native service evidence.
A reviewer can propose an improvement from a failing or missing finding,
approve or reject it, record a simulated execution, verify the outcome, and
inspect the resulting audit history.

Execution is explicitly simulated. It does not connect to infrastructure,
change production configuration, or claim a production deployment.

## API journey

The FastAPI interface exposes session, recommendation, approval, rejection,
execution, verification, and event endpoints. Request identifiers provide
idempotency. Session identifiers scope every workflow read and write.

The public API uses the in memory demonstration store by default. PostgreSQL
is available through the `postgres` workflow mode after its migration is
applied and its restricted runtime role is configured.

## Verification boundary

The workflow tests cover valid transitions, rejected transitions, duplicate
requests, missing services, passing evidence, and cross session isolation.
API tests cover the complete journey and its failure paths.

A browser test exercises the visible catalog journey from recommendation
through verified status and audit history. It does not establish complete
application accessibility or production durability.

## Remaining phase three work

The PostgreSQL migration must be applied and verified. Documentation,
repository governance, and the complete local check must then be updated.
Restricted runtime credentials and public hosted session isolation remain
part of the deployment hardening work.
