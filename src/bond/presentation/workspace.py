"""Evidence inspection workspace. Synthetic data and no production actions."""

from html import escape
from uuid import uuid4

import streamlit as st

from bond.application import CatalogApplication, OrganizationSnapshot, ServiceAssessment
from bond.application_workflow import AssuranceWorkflow
from bond.demo import warehouse_fixture
from bond.domain.models import RuleStatus
from bond.domain.rules import summarize
from bond.domain.workflow import (
    ExecutionRecord,
    RecommendationDraft,
    VerificationRecord,
    WorkflowDecision,
    WorkflowStatus,
)
from bond.presentation.data_views import render_line_chart, render_table
from bond.presentation.explorer import NATIVE_SELECTION_KEY, render_explorer
from bond.presentation.refinements import apply_refinements
from bond.presentation.styles import apply_styles, load_tokens
from bond.repositories.fixtures import FixtureCatalogRepository
from bond.workflow_runtime import MEMORY_MODE, build_workflow_runtime

PAGES = (
    "Scorecard Console",
    "Catalog Repository",
    "Pipeline Laboratory",
    "Engineering Notes",
)

WORKFLOW_SESSION_KEY = "assurance_session_id"


def _workflow() -> AssuranceWorkflow:
    if WORKFLOW_SESSION_KEY not in st.session_state:
        runtime = build_workflow_runtime(MEMORY_MODE)
        session_id = uuid4()
        runtime.open_session(session_id)
        st.session_state[WORKFLOW_SESSION_KEY] = session_id
        st.session_state["assurance_workflow"] = runtime.application
    return st.session_state["assurance_workflow"]


def _open_service(service_id: str) -> None:
    st.session_state["workspace_page"] = "Catalog Repository"
    st.session_state["catalog_requested_service"] = service_id
    st.session_state["catalog_search"] = ""
    st.session_state["catalog_owner"] = "All owners"
    st.session_state["catalog_result_filter"] = "All results"


def page_header(eyebrow: str, title: str, description: str) -> None:
    st.html(f'<div class="bond-eyebrow">{escape(eyebrow)}</div>')
    st.title(title)
    st.html(f'<p class="bond-introduction">{escape(description)}</p>')


def service_table(assessments: tuple[ServiceAssessment, ...]) -> None:
    rows = [
        {
            "Service": item.service.name,
            "Owner": item.service.owner or "Unassigned",
            "Tier": item.service.tier,
            "Score": (
                f"{item.summary.score_percent:.1f}%"
                if item.summary.score_percent is not None
                else "No score"
            ),
            "Failing rules": item.summary.failed,
            "Missing evidence": item.summary.unknown,
        }
        for item in assessments
    ]
    if not rows:
        st.info("No services match this view. Change the search or filters.")
        return
    render_table(rows, hide_index=True, width="stretch")


def render_scorecard(snapshot: OrganizationSnapshot) -> None:
    page_header(
        "Organization assurance",
        "Scorecard Console",
        "Understand maturity, find accountable owners, "
        "and move directly to the evidence behind a finding.",
    )

    columns = st.columns(4)
    score = snapshot.summary.score_percent
    coverage = snapshot.summary.evidence_coverage_percent

    columns[0].metric("Maturity score", f"{score:.1f}%" if score is not None else "No score")
    columns[1].metric(
        "Evidence coverage",
        f"{coverage:.1f}%" if coverage is not None else "No evidence",
    )
    columns[2].metric(
        "Owned services",
        f"{snapshot.owned_service_count} / {snapshot.service_count}",
    )
    columns[3].metric("Failing rules", snapshot.summary.failed)

    st.caption(
        "Three equally weighted rules per service. Missing evidence remains in the "
        "score denominator and never counts as passing."
    )

    with st.expander("Understand the score"):
        st.write(
            f"{snapshot.summary.passed} passing results, "
            f"{snapshot.summary.failed} failing results, and "
            f"{snapshot.summary.unknown} unknown results across "
            f"{snapshot.summary.total} gates."
        )
        st.write(
            "Maturity is passing gates divided by all gates. Evidence coverage is known "
            "results divided by all gates. Neither measure proves production readiness."
        )

    st.subheader("Attention queue")
    attention = sorted(
        (
            item
            for item in snapshot.assessments
            if item.summary.failed > 0 or item.summary.unknown > 0
        ),
        key=lambda item: (-item.summary.failed, -item.summary.unknown, item.service.name),
    )

    if not attention:
        st.info("No failing or unknown results exist in the current evidence.")

    for item in attention:
        with st.container(border=True):
            detail, action = st.columns([4, 1])
            with detail:
                st.write(item.service.name)
                st.caption(
                    f"Owner: {item.service.owner or 'Unassigned'} · "
                    f"{item.summary.failed} failing · {item.summary.unknown} missing"
                )
            with action:
                st.button(
                    "Inspect evidence",
                    key=f"attention_{item.service.id}",
                    on_click=_open_service,
                    args=(item.service.id,),
                )

    st.subheader("Service maturity")
    service_table(snapshot.assessments)

    with st.container(border=True):
        st.subheader("The assurance boundary")
        st.write(
            "Findings are inspectable today. Recommendations, approval, simulated execution, "
            "and independent verification are the next workflow layer."
        )


def _matches_result(item: ServiceAssessment, result_filter: str) -> bool:
    if result_filter == "Needs attention":
        return item.summary.failed > 0
    if result_filter == "Missing evidence":
        return item.summary.unknown > 0
    if result_filter == "Passing":
        return item.summary.total > 0 and item.summary.failed == 0 and item.summary.unknown == 0
    return True


def _filtered_snapshot(
    assessments: tuple[ServiceAssessment, ...],
) -> OrganizationSnapshot:
    return OrganizationSnapshot(
        assessments=assessments,
        summary=summarize(result for assessment in assessments for result in assessment.results),
    )


def _workflow_status_label(status: WorkflowStatus) -> str:
    return {
        WorkflowStatus.PROPOSED: "Proposed",
        WorkflowStatus.APPROVED: "Approved",
        WorkflowStatus.REJECTED: "Rejected",
        WorkflowStatus.EXECUTED: "Simulated action recorded",
        WorkflowStatus.VERIFIED: "Verified",
        WorkflowStatus.REVIEW_REQUIRED: "Review required",
    }[status]


def _render_workflow(selected: ServiceAssessment) -> None:
    workflow = _workflow()
    session_id = st.session_state[WORKFLOW_SESSION_KEY]
    service = selected.service

    st.subheader("Improvement workflow")
    st.caption(
        "Recommendations are session isolated. Execution is simulated and "
        "never changes production infrastructure."
    )

    recommendations = workflow.recommendations(session_id)
    service_recommendations = tuple(
        item for item in recommendations if item.service_id == service.id
    )

    failing_or_unknown = tuple(
        result for result in selected.results if result.status is not RuleStatus.PASS
    )

    if failing_or_unknown:
        with st.form("create_recommendation", border=True):
            rule = st.selectbox(
                "Evidence finding",
                failing_or_unknown,
                format_func=lambda item: f"{item.rule_id} · {item.status.value}",
            )
            title = st.text_input(
                "Recommendation title",
                value=f"Address {rule.rule_id} for {service.name}",
            )
            detail = st.text_area(
                "Why this action is recommended",
                value=rule.explanation,
            )
            expected = st.text_area(
                "Expected verified result",
                value="The selected evidence finding is resolved.",
            )
            submitted = st.form_submit_button("Propose recommendation")

        if submitted:
            try:
                workflow.propose(
                    session_id,
                    RecommendationDraft(
                        service_id=service.id,
                        rule_id=rule.rule_id,
                        rule_version=rule.version,
                        title=title,
                        detail=detail,
                        owner=service.owner,
                        expected_result=expected,
                    ),
                    uuid4(),
                )
                st.success("Recommendation proposed in this demonstration session.")
                st.rerun()
            except ValueError as error:
                st.error(str(error))
    else:
        st.info("No failing or missing evidence is available for a new recommendation.")

    if not service_recommendations:
        st.caption("No recommendations exist for this service in this session.")
        return

    for item in service_recommendations:
        with st.container(border=True):
            status = _workflow_status_label(item.status)
            st.write(f"**{item.title}** · {status}")
            st.caption(
                f"Rule {item.rule_id} · Version {item.rule_version} · "
                f"Owner {item.owner or 'Unassigned'}"
            )
            st.write(item.detail)
            st.write(f"Expected result: {item.expected_result}")

            if item.status is WorkflowStatus.PROPOSED:
                approval, rejection = st.columns(2)
                with approval:
                    if st.button("Approve", key=f"approve_{item.id}"):
                        workflow.approve(
                            item.id,
                            session_id,
                            WorkflowDecision(
                                actor="Demonstration approver",
                                reason="Approved for simulated execution.",
                                request_id=uuid4(),
                            ),
                        )
                        st.rerun()
                with rejection:
                    if st.button("Reject", key=f"reject_{item.id}"):
                        workflow.reject(
                            item.id,
                            session_id,
                            WorkflowDecision(
                                actor="Demonstration approver",
                                reason="Rejected in this demonstration session.",
                                request_id=uuid4(),
                            ),
                        )
                        st.rerun()

            elif item.status is WorkflowStatus.APPROVED:
                if st.button("Record simulated execution", key=f"execute_{item.id}"):
                    workflow.execute(
                        item.id,
                        session_id,
                        ExecutionRecord(
                            actor="Demonstration automation",
                            simulated_command="apply_documented_improvement",
                            reason="The approved action is simulated.",
                            request_id=uuid4(),
                        ),
                    )
                    st.rerun()

            elif item.status is WorkflowStatus.EXECUTED:
                verified, review = st.columns(2)
                with verified:
                    if st.button("Verify success", key=f"verify_{item.id}"):
                        workflow.verify(
                            item.id,
                            session_id,
                            VerificationRecord(
                                actor="Demonstration reviewer",
                                observed_result="The expected evidence change was observed.",
                                passed=True,
                                reason="The expected result was confirmed.",
                                request_id=uuid4(),
                            ),
                        )
                        st.rerun()
                with review:
                    if st.button("Send for review", key=f"review_{item.id}"):
                        workflow.verify(
                            item.id,
                            session_id,
                            VerificationRecord(
                                actor="Demonstration reviewer",
                                observed_result="The expected evidence change was not observed.",
                                passed=False,
                                reason="Additional review is required.",
                                request_id=uuid4(),
                            ),
                        )
                        st.rerun()

            with st.expander("Audit history"):
                events = workflow.history(item.id, session_id)
                if not events:
                    st.caption("No workflow events are recorded yet.")
                for event in events:
                    st.write(
                        f"{event.occurred_at.strftime('%Y-%m-%d %H:%M:%S')} · "
                        f"{event.kind.value} · {event.actor}"
                    )
                    st.caption(event.detail)


def _native_service_detail(
    selected: ServiceAssessment,
    snapshot: OrganizationSnapshot,
) -> None:
    with st.container(border=True):
        st.subheader(selected.service.name)
        st.write(selected.service.description)
        st.caption(
            f"Owner: {selected.service.owner or 'Unassigned'} · "
            f"Tier {selected.service.tier} · Synthetic source"
        )

        for result in selected.results:
            label = {
                RuleStatus.PASS: "Pass",
                RuleStatus.FAIL: "Needs attention",
                RuleStatus.UNKNOWN: "Missing evidence",
            }[result.status]
            st.html(
                f'<span class="bond-status bond-{escape(result.status.value)}">'
                f"{escape(label)}</span>"
            )
            st.write(result.explanation)
            st.caption(f"Rule: {result.rule_id} · Version: {result.version}")

        names = {item.service.id: item.service.name for item in snapshot.assessments}
        dependencies = [
            names.get(identifier, identifier) for identifier in selected.service.dependencies
        ]
        st.write("Dependencies")
        st.write(", ".join(dependencies) if dependencies else "No dependencies recorded")
        st.caption(
            "Fixed observation: "
            + selected.service.observed_at.isoformat()
            + ". Not a live production observation."
        )

    _render_workflow(selected)


def render_catalog(snapshot: OrganizationSnapshot) -> None:
    page_header(
        "Service context",
        "Catalog Repository",
        "Follow a service from ownership and dependencies to the rule evidence that needs review.",
    )

    search = st.text_input(
        "Search services",
        placeholder="Search by service name or owner",
        key="catalog_search",
    )

    owners = sorted(
        {item.service.owner for item in snapshot.assessments if item.service.owner is not None}
    )

    first, second = st.columns(2)
    with first:
        owner = st.selectbox(
            "Owner",
            ["All owners", "Unassigned", *owners],
            key="catalog_owner",
        )
    with second:
        result_filter = st.selectbox(
            "Rule results",
            ["All results", "Needs attention", "Missing evidence", "Passing"],
            key="catalog_result_filter",
        )

    query = search.strip().casefold()
    matching = tuple(
        item
        for item in snapshot.assessments
        if (
            not query
            or query in item.service.name.casefold()
            or query in (item.service.owner or "").casefold()
        )
        and (
            owner == "All owners"
            or (owner == "Unassigned" and item.service.owner is None)
            or item.service.owner == owner
        )
        and _matches_result(item, result_filter)
    )

    st.caption(f"{len(matching)} of {snapshot.service_count} services in this view")
    service_table(matching)

    if not matching:
        return

    names = {item.service.id: item.service.name for item in matching}
    selected_key = NATIVE_SELECTION_KEY
    requested = st.session_state.pop("catalog_requested_service", None)
    existing = st.session_state.get(selected_key)

    if isinstance(requested, str) and requested in names:
        st.session_state[selected_key] = requested
    elif not isinstance(existing, str) or existing not in names:
        st.session_state[selected_key] = next(iter(names))

    native_only = st.toggle(
        "Use native evidence view",
        value=False,
        key="native_evidence_only",
        help="The native service inspector remains available without the React explorer.",
    )

    if not native_only:
        selection = st.session_state.get(selected_key)
        selected_id = selection if isinstance(selection, str) and selection in names else None
        event = render_explorer(_filtered_snapshot(matching), selected_id)
        if event is not None:
            st.session_state[selected_key] = event.service_id

    st.subheader("Native service inspection")
    st.caption("This inspection path does not depend on the custom component.")

    selected_id = st.selectbox(
        "Inspect service",
        list(names),
        format_func=lambda identifier: names[identifier],
        key=selected_key,
    )

    selected = next(item for item in matching if item.service.id == selected_id)
    _native_service_detail(selected, snapshot)


def render_pipeline() -> None:
    window = warehouse_fixture()
    tokens = load_tokens()

    page_header(
        "Warehouse evidence",
        "Pipeline Laboratory",
        "Inspect warehouse consumption and query behavior without confusing "
        "synthetic evidence with live activity.",
    )

    p95 = window.p95_ms
    columns = st.columns(3)
    columns[0].metric("Warehouse credits", f"{window.credits_consumed:.2f}")
    columns[1].metric("Credit burn per hour", f"{window.credits_per_hour:.2f}")
    columns[2].metric("P95 query latency", f"{p95:.0f} ms" if p95 is not None else "No samples")

    st.caption(
        f"{window.warehouse} · Synthetic source · "
        f"{window.window_seconds} second window · "
        f"{len(window.latencies_ms)} samples"
    )

    st.subheader("Query latency")
    render_line_chart(
        {"Latency in milliseconds": list(window.latencies_ms)},
        color=tokens.primitives["violet"],
        height=260,
    )

    threshold = st.number_input(
        "Review threshold in milliseconds",
        min_value=1,
        value=300,
        step=50,
    )
    only_above = st.toggle("Show only samples above the review threshold", value=False)
    st.caption("Exploratory filter only. It does not change policy or persisted evidence.")

    rows = [
        {
            "Query sample": f"DEMO_{index:03d}",
            "Latency in milliseconds": latency,
            "Review state": "Above threshold" if latency > threshold else "Within threshold",
            "Source": "Synthetic",
        }
        for index, latency in enumerate(window.latencies_ms, start=1)
        if not only_above or latency > threshold
    ]

    st.caption(f"Showing {len(rows)} of {len(window.latencies_ms)} query samples")

    if rows:
        render_table(rows, hide_index=True, width="stretch")
    else:
        st.info("No query samples exceed the current review threshold.")

    with st.expander("Measurement method and source"):
        st.write(
            "P95 uses nearest rank over the ten fixed samples. Warehouse credits "
            "are consumption units, not money. The threshold is an inspection aid, "
            "not an approved engineering policy."
        )
        st.caption("Fixed observation: " + window.observed_at.isoformat())

    with st.container(border=True):
        st.subheader("Connection pool telemetry")
        st.write(
            "Application pool telemetry is not connected yet. "
            "Warehouse samples cannot establish application connection pool size."
        )

    st.info(
        "Recommendation approval, simulated changes, and independent verification "
        "remain part of the next workflow phase."
    )


def render_notes() -> None:
    page_header(
        "Inspect the engineering",
        "Engineering Notes",
        "Understand what works, what is simulated, and where the engineering evidence lives.",
    )

    with st.container(border=True):
        st.subheader("Independent demonstration")
        st.write(
            "BOND is an independent portfolio project. It is not an official Cortex "
            "product and does not imply endorsement."
        )

    st.subheader("Current operating mode")
    st.write(
        "The interface and API use packaged synthetic fixtures. PostgreSQL schema "
        "and repository operations were verified separately through operator commands. "
        "The public interface does not use administrative database credentials."
    )

    st.subheader("Architecture")
    st.code(
        "Streamlit workspace and React evidence explorer\n"
        "                    |\n"
        " Shared application services / FastAPI interface\n"
        "                    |\n"
        "       Typed contracts and domain rules\n"
        "                    |\n"
        "           Repository interfaces\n"
        "                    |\n"
        "     Fixture adapter / PostgreSQL adapter",
        language=None,
    )

    with st.expander("Hosting and availability"):
        st.write(
            "The submission targets free Streamlit and Supabase allowances. "
            "Services may sleep, pause, or impose resource limits. Continuous "
            "availability and production capacity are not established."
        )

    with st.expander("Security boundaries"):
        st.write(
            "The recorded client database connection passed certificate and hostname "
            "verification. The separate pooler to PostgreSQL link was not reported "
            "as TLS. Restricted runtime access and public session isolation remain "
            "to be implemented and tested."
        )
        st.write(
            "The React component can request inspection of a known service. "
            "That request does not authorize an infrastructure action. "
            "Style isolation is not a security sandbox."
        )

    with st.expander("Evidence and verification"):
        st.write(
            "The foundation recorded 57 passing tests. Later component checks "
            "expanded the suite. Consult the repository and actual workflow runs "
            "for current results rather than treating a static count as a live status."
        )

    st.link_button("Inspect the repository", "https://github.com/FriesRdBest/BOND")


def main() -> None:
    st.set_page_config(
        page_title="BOND | Engineering assurance",
        page_icon="◈",
        layout="wide",
    )
    apply_styles()
    apply_refinements()

    if "workspace_page" not in st.session_state:
        destinations = {
            "scorecard": "Scorecard Console",
            "catalog": "Catalog Repository",
            "pipeline": "Pipeline Laboratory",
            "engineering": "Engineering Notes",
        }
        requested_view = st.query_params.get("view")
        st.session_state["workspace_page"] = (
            destinations.get(requested_view, "Scorecard Console")
            if isinstance(requested_view, str)
            else "Scorecard Console"
        )

    with st.sidebar:
        st.title("BOND")
        st.caption("Engineering assurance workbench")
        page = st.radio("Workspace", PAGES, key="workspace_page")
        st.divider()
        st.caption("Synthetic evidence")
        st.caption("Independent portfolio demonstration")
        st.link_button("Source repository", "https://github.com/FriesRdBest/BOND")

    st.html(
        '<div class="bond-contextbar">'
        "<span><strong>Demonstration</strong> · Fixed synthetic evidence</span>"
        "<span>No production actions</span>"
        "</div>"
    )

    if page == "Pipeline Laboratory":
        render_pipeline()
    elif page == "Engineering Notes":
        render_notes()
    else:
        snapshot = CatalogApplication(FixtureCatalogRepository()).snapshot()
        if page == "Scorecard Console":
            render_scorecard(snapshot)
        else:
            render_catalog(snapshot)
