ALTER TABLE bond.demo_sessions ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON bond.demo_sessions FROM PUBLIC;

CREATE TABLE bond.improvements (
    id uuid PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES bond.demo_sessions(session_id)
        ON DELETE CASCADE,
    service_id text NOT NULL,
    rule_id text NOT NULL,
    rule_version text NOT NULL,
    title text NOT NULL,
    detail text NOT NULL,
    owner text,
    expected_result text NOT NULL,
    status text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT improvements_status_allowed CHECK (
        status IN (
            'proposed',
            'approved',
            'rejected',
            'executed',
            'verified',
            'review_required'
        )
    ),
    CONSTRAINT improvements_service_identifier CHECK (
        service_id ~ '^[a-z][a-z0-9_]{2,63}$'
    ),
    CONSTRAINT improvements_rule_identifier CHECK (
        rule_id ~ '^[a-z][a-z0-9_]{2,63}$'
    ),
    CONSTRAINT improvements_id_session_unique
        UNIQUE (id, session_id)
);

CREATE INDEX improvements_session_created_idx
    ON bond.improvements (session_id, created_at DESC);

CREATE TABLE bond.workflow_events (
    id uuid PRIMARY KEY,
    improvement_id uuid NOT NULL,
    session_id uuid NOT NULL REFERENCES bond.demo_sessions(session_id)
        ON DELETE CASCADE,
    kind text NOT NULL,
    actor text NOT NULL,
    detail text NOT NULL,
    request_id uuid NOT NULL,
    occurred_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT workflow_event_kind_allowed CHECK (
        kind IN (
            'recommendation_created',
            'approval_granted',
            'recommendation_rejected',
            'simulated_execution_recorded',
            'verification_passed',
            'verification_failed'
        )
    ),
    CONSTRAINT workflow_events_request_unique
        UNIQUE (improvement_id, request_id),
    CONSTRAINT workflow_events_improvement_session
        FOREIGN KEY (improvement_id, session_id)
        REFERENCES bond.improvements(id, session_id)
        ON DELETE CASCADE
);

CREATE INDEX workflow_events_improvement_time_idx
    ON bond.workflow_events (improvement_id, occurred_at);

ALTER TABLE bond.improvements ENABLE ROW LEVEL SECURITY;
ALTER TABLE bond.workflow_events ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON bond.improvements FROM PUBLIC;
REVOKE ALL ON bond.workflow_events FROM PUBLIC;
