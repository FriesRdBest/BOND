"""Shared application and telemetry fixture tests."""

from bond.application import CatalogApplication
from bond.demo import warehouse_fixture
from bond.repositories.fixtures import FixtureCatalogRepository


def test_snapshot_summarizes_all_service_rules() -> None:
    snapshot = CatalogApplication(FixtureCatalogRepository()).snapshot()
    assert snapshot.service_count == 6
    assert snapshot.owned_service_count == 5
    assert snapshot.summary.total == 18
    assert snapshot.summary.passed == 13
    assert snapshot.summary.failed == 3
    assert snapshot.summary.unknown == 2


def test_missing_service_has_no_assessment() -> None:
    application = CatalogApplication(FixtureCatalogRepository())
    assert application.assess("not_present") is None


def test_single_service_assessment() -> None:
    assessment = CatalogApplication(FixtureCatalogRepository()).assess("billing_export")
    assert assessment is not None
    assert assessment.summary.failed == 2


def test_warehouse_fixture_is_explicitly_synthetic() -> None:
    window = warehouse_fixture()
    assert window.source == "synthetic"
    assert len(window.latencies_ms) == 10
    assert window.p95_ms == 870
    assert str(window.credits_per_hour) == "2.40"
