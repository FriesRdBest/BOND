# BOND security and data handling

## Scope

This document records requirements, not a security certification. The initial project advisor returned no notices, but application authorization, schema permissions, isolation, and connection authentication remain unverified until tested.

## Secrets

Keep passwords, secret API keys, and credentials out of Git, logs, screenshots, documentation, and conversation. Codespaces secrets and Streamlit secrets are separate configurations. Validate presence without printing values. The application does not need the Supabase publishable key for its planned PostgreSQL connection.

## Database access

Use administrative access only for controlled setup and migrations. Create a restricted runtime role before deployment. Define explicit grants and test denied operations. Keep Data API exposure unnecessary for this architecture. The owner was instructed to disable it, but the setting still requires verification.

## Demo protection

Use synthetic data, isolate visitor state, constrain public actions, and label simulation. Approval controls must be enforced by application logic and supported by database constraints where appropriate. Hidden buttons are not authorization.

## Verification

Check authorization boundaries, invalid transitions, injection risks, sensitive logs, dependency findings, repeated requests, and recovery. Use CodeQL and other applicable checks when configured. Document unresolved findings and avoid claiming that the presence of a tool proves safety.

## Reporting

Do not publish credentials in issues. Use the repository private vulnerability reporting channel if enabled. If unavailable, use a private contact method published by the owner. A dedicated reporting address and verified private reporting configuration remain to be established before submission.

## Incident response

If a credential is exposed, revoke or rotate it, assess affected access, and remove the exposed value from active configuration. Removing a file alone does not invalidate a credential. Record the event without reproducing the secret.
