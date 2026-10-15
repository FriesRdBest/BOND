-- Requires the bond_app login role to exist before this migration is applied.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'bond_app'
    ) THEN
        RAISE EXCEPTION
            'Create the bond_app login role before applying migration 0003.';
    END IF;
END
$$;

GRANT USAGE ON SCHEMA bond TO bond_app;

GRANT SELECT ON bond.catalog TO bond_app;

GRANT SELECT, INSERT, UPDATE, DELETE ON bond.demo_sessions TO bond_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON bond.improvements TO bond_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON bond.workflow_events TO bond_app;
GRANT SELECT, INSERT ON bond.audit_events TO bond_app;

CREATE POLICY catalog_readable_by_runtime
    ON bond.catalog
    FOR SELECT
    TO bond_app
    USING (true);

CREATE POLICY runtime_session_isolation
    ON bond.demo_sessions
    FOR ALL
    TO bond_app
    USING (
        session_id = current_setting('bond.session_id', true)::uuid
    )
    WITH CHECK (
        session_id = current_setting('bond.session_id', true)::uuid
    );

CREATE POLICY runtime_recommendation_isolation
    ON bond.improvements
    FOR ALL
    TO bond_app
    USING (
        session_id = current_setting('bond.session_id', true)::uuid
    )
    WITH CHECK (
        session_id = current_setting('bond.session_id', true)::uuid
    );

CREATE POLICY runtime_workflow_event_isolation
    ON bond.workflow_events
    FOR ALL
    TO bond_app
    USING (
        session_id = current_setting('bond.session_id', true)::uuid
    )
    WITH CHECK (
        session_id = current_setting('bond.session_id', true)::uuid
    );

CREATE POLICY runtime_audit_event_isolation
    ON bond.audit_events
    FOR SELECT
    TO bond_app
    USING (
        session_id = current_setting('bond.session_id', true)::uuid
    );

CREATE POLICY runtime_audit_event_insert
    ON bond.audit_events
    FOR INSERT
    TO bond_app
    WITH CHECK (
        session_id = current_setting('bond.session_id', true)::uuid
    );
