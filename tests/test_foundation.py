"""Deterministic foundation checks without external services."""

import json
from decimal import Decimal
from importlib.resources import files

import pytest
from pydantic import ValidationError

from bond.domain.models import RuleStatus, Service
from bond.domain.rules import evaluate_service, summarize
from bond.domain.telemetry import hourly_credit_burn, p95_latency_ms
from bond.repositories.fixtures import FixtureCatalogRepository
from bond.repositories.interfaces import CatalogRepository


def test_catalog_implements_repository_contract() -> None:
    repository: CatalogRepository = FixtureCatalogRepository()
    assert len(repository.list_services()) == 6
    assert repository.get_service("not_present") is None


def test_catalog_is_deterministic() -> None:
    assert FixtureCatalogRepository().list_services() == FixtureCatalogRepository().list_services()


def test_fully_passing_service() -> None:
    service = FixtureCatalogRepository().list_services()[0]
    results = evaluate_service(service)
    assert all(result.status == RuleStatus.PASS for result in results)
    assert summarize(results).score_percent == 100


def test_missing_evidence_is_not_a_pass() -> None:
    service = FixtureCatalogRepository().get_service("policy_evaluator")
    assert service is not None
    summary = summarize(evaluate_service(service))
    assert summary.unknown == 1
    assert summary.score_percent == 66.7
    assert summary.evidence_coverage_percent == 66.7


def test_unowned_vulnerable_service_fails_two_rules() -> None:
    service = FixtureCatalogRepository().get_service("billing_export")
    assert service is not None
    summary = summarize(evaluate_service(service))
    assert summary.failed == 2
    assert summary.passed == 1


def test_empty_score_is_not_a_perfect_score() -> None:
    summary = summarize(())
    assert summary.score_percent is None
    assert summary.evidence_coverage_percent is None


def test_domain_values_are_frozen() -> None:
    service = FixtureCatalogRepository().list_services()[0]
    with pytest.raises(ValidationError):
        service.name = "Changed"


def test_unknown_contract_fields_are_rejected() -> None:
    data = FixtureCatalogRepository().list_services()[0].model_dump()
    data["unexpected"] = True
    with pytest.raises(ValidationError):
        Service.model_validate(data)


def test_observation_requires_timezone() -> None:
    data = FixtureCatalogRepository().list_services()[0].model_dump()
    data["observed_at"] = "2026-10-15T12:00:00"
    with pytest.raises(ValidationError):
        Service.model_validate(data)


def test_negative_vulnerability_count_is_rejected() -> None:
    data = FixtureCatalogRepository().list_services()[0].model_dump()
    data["critical_vulnerabilities"] = -1
    with pytest.raises(ValidationError):
        Service.model_validate(data)


def test_p95_uses_nearest_rank() -> None:
    assert p95_latency_ms(list(range(1, 101))) == 95
    assert p95_latency_ms([4]) == 4
    assert p95_latency_ms([]) is None


@pytest.mark.parametrize("sample", [-1, float("nan"), float("inf")])
def test_invalid_latency_is_rejected(sample: float) -> None:
    with pytest.raises(ValueError):
        p95_latency_ms([sample])


def test_credit_rate_is_not_a_currency_value() -> None:
    assert hourly_credit_burn(Decimal("1.25"), 1800) == Decimal("2.50")


@pytest.mark.parametrize("window", [0, -1])
def test_invalid_credit_window_is_rejected(window: int) -> None:
    with pytest.raises(ValueError):
        hourly_credit_burn(Decimal("1"), window)


def test_negative_credits_are_rejected() -> None:
    with pytest.raises(ValueError):
        hourly_credit_burn(Decimal("-1"), 3600)


def test_token_references_resolve() -> None:
    tokens = json.loads(
        files("bond.data").joinpath("design_tokens.json").read_text(encoding="utf-8")
    )
    assert set(tokens) == {"primitives", "semantic", "components"}
    for primitive in tokens["semantic"].values():
        assert primitive in tokens["primitives"]
    for semantic in tokens["components"].values():
        assert semantic in tokens["semantic"]


def relative_luminance(color: str) -> float:
    channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


@pytest.mark.parametrize("foreground", ["text", "secondary", "muted"])
@pytest.mark.parametrize("background", ["canvas", "surface", "raised"])
def test_normal_text_contrast(foreground: str, background: str) -> None:
    tokens = json.loads(
        files("bond.data").joinpath("design_tokens.json").read_text(encoding="utf-8")
    )
    first = relative_luminance(tokens["primitives"][foreground])
    second = relative_luminance(tokens["primitives"][background])
    contrast = (max(first, second) + 0.05) / (min(first, second) + 0.05)
    assert contrast >= 4.5, f"{foreground} on {background}: {contrast:.2f}"
