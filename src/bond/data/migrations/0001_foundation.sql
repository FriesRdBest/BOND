CREATE SCHEMA bond;

REVOKE ALL ON SCHEMA bond FROM PUBLIC;

CREATE TABLE bond.catalog (
    service_id text PRIMARY KEY
        CHECK (service_id ~ '^[a-z][a-z0-9_]{2,63}$'),
    document jsonb NOT NULL
        CHECK (jsonb_typeof(document) = 'object')
        CHECK (document ? 'id')
        CHECK (document ->> 'id' = service_id),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE bond.demo_sessions (
    session_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fixture_version text NOT NULL DEFAULT '1',
    created_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL DEFAULT (now() + interval '24 hours'),
    CHECK (expires_at > created_at)
);

CREATE TABLE bond.audit_events (
    event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id uuid NOT NULL REFERENCES bond.demo_sessions(session_id),
    event_type text NOT NULL
        CHECK (char_length(event_type) BETWEEN 1 AND 80),
    payload jsonb NOT NULL
        CHECK (jsonb_typeof(payload) = 'object'),
    idempotency_key text
        CHECK (char_length(idempotency_key) BETWEEN 1 AND 160),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (session_id, idempotency_key)
);

CREATE INDEX audit_events_session_time_idx
    ON bond.audit_events (session_id, created_at, event_id);

CREATE INDEX demo_sessions_expiry_idx
    ON bond.demo_sessions (expires_at);

ALTER TABLE bond.catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE bond.demo_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE bond.audit_events ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON ALL TABLES IN SCHEMA bond FROM PUBLIC;

DO $permissions$
DECLARE
    role_name text;
BEGIN
    FOREACH role_name IN ARRAY ARRAY['anon', 'authenticated', 'service_role']
    LOOP
        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = role_name) THEN
            EXECUTE format('REVOKE ALL ON SCHEMA bond FROM %I', role_name);
            EXECUTE format(
                'REVOKE ALL ON ALL TABLES IN SCHEMA bond FROM %I',
                role_name
            );
        END IF;
    END LOOP;
END
$permissions$;
