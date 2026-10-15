"""Initial review workspace. Synthetic evidence only."""

from html import escape

import streamlit as st

from bond.application import CatalogApplication, OrganizationSnapshot, ServiceAssessment
from bond.demo import warehouse_fixture
from bond.domain.models import RuleStatus
from bond.presentation.data_views import render_line_chart, render_table
from bond.presentation.styles import apply_styles, load_tokens
from bond.repositories.fixtures import FixtureCatalogRepository

PAGES = (
    "Scorecard Console",
    "Catalog Repository",
    "Pipeline Laboratory",
    "Engineering Notes",
)


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
            "Score": f"{item.summary.score_percent:.1f}%",
            "Failing rules": item.summary.failed,
            "Missing evidence": item.summary.unknown,
        }
        for item in assessments
    ]
    if not rows:
        st.info("No services match this view.")
        return
    render_table(rows, hide_index=True, width="stretch")


def render_scorecard(snapshot: OrganizationSnapshot) -> None:
    page_header(
        "Organization assurance",
        "Scorecard Console",
        "Understand maturity, identify ownership gaps, "
        "and inspect the evidence behind each result.",
    )

    columns = st.columns(4)
    columns[0].metric("Maturity score", f"{snapshot.summary.score_percent:.1f}%")
    columns[1].metric(
        "Evidence coverage",
        f"{snapshot.summary.evidence_coverage_percent:.1f}%",
    )
    columns[2].metric(
        "Owned services",
        f"{snapshot.owned_service_count} / {snapshot.service_count}",
    )
    columns[3].metric("Failing rules", snapshot.summary.failed)

    st.caption(
        "Three equally weighted rules per service. Missing evidence does not count as a pass."
    )
    st.subheader("Service maturity")
    service_table(snapshot.assessments)

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.subheader("What the score means")
            st.write(
                "The score is the share of all evaluated gates that pass. "
                "Evidence coverage separately shows which gates have a known result."
            )
    with right:
        with st.container(border=True):
            st.subheader("From evidence to action")
            st.write(
                "This foundation makes findings inspectable. Approval, simulated action, "
                "and independent verification will complete the assurance journey."
            )


def render_catalog(snapshot: OrganizationSnapshot) -> None:
    page_header(
        "Service context",
        "Catalog Repository",
        "Connect service identity, ownership, dependencies, and policy evidence.",
    )

    search = st.text_input("Search services", placeholder="Search by service name or owner")
    owners = sorted(
        {
            assessment.service.owner
            for assessment in snapshot.assessments
            if assessment.service.owner is not None
        }
    )
    owner = st.selectbox("Owner", ["All owners", "Unassigned", *owners])
    query = search.strip().casefold()

    matching = tuple(
        assessment
        for assessment in snapshot.assessments
        if (
            not query
            or query in assessment.service.name.casefold()
            or query in (assessment.service.owner or "").casefold()
        )
        and (
            owner == "All owners"
            or (owner == "Unassigned" and assessment.service.owner is None)
            or assessment.service.owner == owner
        )
    )

    service_table(matching)

    if not matching:
        return

    names = {assessment.service.id: assessment.service.name for assessment in matching}
    selected_id = st.selectbox(
        "Inspect service",
        list(names),
        format_func=lambda service_id: names[service_id],
    )
    selected = next(assessment for assessment in matching if assessment.service.id == selected_id)

    with st.container(border=True):
        st.subheader(selected.service.name)
        st.write(selected.service.description)
        st.caption(
            f"Owner: {selected.service.owner or 'Unassigned'} · "
            f"Tier {selected.service.tier} · Source: synthetic"
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

        dependencies = ", ".join(selected.service.dependencies) or "No dependencies recorded"
        st.write("Dependencies")
        st.code(dependencies, language=None)
        st.caption(
            "Fixed fixture observation: "
            + selected.service.observed_at.isoformat()
            + ". This is not a live production observation."
        )


def render_pipeline() -> None:
    window = warehouse_fixture()
    tokens = load_tokens()

    page_header(
        "Warehouse evidence",
        "Pipeline Laboratory",
        "Inspect a reproducible warehouse window with explicit units and measurement rules.",
    )

    columns = st.columns(3)
    columns[0].metric("Warehouse credits", f"{window.credits_consumed:.2f}")
    columns[1].metric("Credit burn per hour", f"{window.credits_per_hour:.2f}")
    columns[2].metric("P95 query latency", f"{window.p95_ms:.0f} ms")

    st.caption(
        f"Synthetic warehouse: {window.warehouse} · "
        f"{window.window_seconds} second window · "
        f"{len(window.latencies_ms)} query samples"
    )

    st.subheader("Query latency samples")
    render_line_chart(
        {"Latency in milliseconds": list(window.latencies_ms)},
        color=tokens.primitives["violet"],
        height=260,
    )

    render_table(
        [
            {
                "Query sample": f"DEMO_{index:03d}",
                "Latency in milliseconds": latency,
                "Source": "Synthetic",
            }
            for index, latency in enumerate(window.latencies_ms, start=1)
        ],
        hide_index=True,
        width="stretch",
    )

    with st.container(border=True):
        st.subheader("Measurement boundaries")
        st.write(
            "P95 uses nearest rank over the ten displayed samples. "
            "Credits describe warehouse consumption, not money. "
            "Application connection pool size is a different metric and is not "
            "invented from this warehouse fixture."
        )
        st.caption("Fixed observation: " + window.observed_at.isoformat())

    st.info(
        "Ingestion scheduling, golden path recommendations, and action verification "
        "are not implemented in this foundation."
    )


def render_notes() -> None:
    page_header(
        "Inspect the engineering",
        "Engineering Notes",
        "A transparent account of the current demonstration and its intended boundaries.",
    )

    st.subheader("Independent demonstration")
    st.write(
        "BOND is an independent portfolio project. It is not an official Cortex product "
        "and does not imply endorsement."
    )

    st.subheader("Current mode")
    st.write(
        "The interface and API read packaged synthetic fixtures. "
        "Database migrations and the PostgreSQL adapter are exercised separately "
        "through operator commands. The public interface does not use administrative credentials."
    )

    st.subheader("Architecture")
    st.code(
        "Streamlit presentation / FastAPI entry point\n"
        "                    |\n"
        "          Shared application services\n"
        "                    |\n"
        "        Typed contracts and domain rules\n"
        "                    |\n"
        "            Repository interfaces\n"
        "                    |\n"
        "      Fixture adapter / PostgreSQL adapter",
        language=None,
    )

    st.subheader("Availability and limitations")
    st.write(
        "The submission targets free hosting allowances. Services may sleep, pause, "
        "or impose resource limits. This foundation does not establish continuous "
        "availability, production capacity, or a completed approval workflow."
    )

    st.subheader("Security observation")
    st.write(
        "The initial operator connection passed client certificate and hostname verification. "
        "The separate pooler to PostgreSQL link was not reported as TLS by the database view. "
        "Runtime permissions and demo isolation still require implementation and testing."
    )

    st.link_button("Inspect the repository", "https://github.com/FriesRdBest/BOND")


def main() -> None:
    st.set_page_config(
        page_title="BOND | Engineering assurance",
        page_icon="◈",
        layout="wide",
    )
    apply_styles()

    with st.sidebar:
        st.title("BOND")
        st.caption("Engineering assurance workbench")
        page = st.radio("Workspace", PAGES, key="workspace_page")
        st.divider()
        st.caption("Synthetic evidence")
        st.caption("Independent portfolio demonstration")
        st.link_button("Source repository", "https://github.com/FriesRdBest/BOND")

    st.caption("DEMONSTRATION · Fixed synthetic evidence · No production actions")
    application = CatalogApplication(FixtureCatalogRepository())

    if page == "Scorecard Console":
        render_scorecard(application.snapshot())
    elif page == "Catalog Repository":
        render_catalog(application.snapshot())
    elif page == "Pipeline Laboratory":
        render_pipeline()
    else:
        render_notes()
