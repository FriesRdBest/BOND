"""Initial equally weighted maturity rules."""

from collections.abc import Iterable

from bond.domain.models import RuleResult, RuleStatus, ScoreSummary, Service


def evaluate_service(service: Service) -> tuple[RuleResult, ...]:
    owner = RuleResult(
        rule_id="ownership_assigned",
        status=RuleStatus.PASS if service.owner else RuleStatus.FAIL,
        explanation=(
            "An accountable owner is assigned." if service.owner else "No owner is assigned."
        ),
    )

    if service.contract_visible is None:
        contract_status = RuleStatus.UNKNOWN
        contract_explanation = "Contract evidence is missing."
    elif service.contract_visible:
        contract_status = RuleStatus.PASS
        contract_explanation = "Contract evidence is visible."
    else:
        contract_status = RuleStatus.FAIL
        contract_explanation = "The service contract is not visible."

    if service.critical_vulnerabilities is None:
        vulnerability_status = RuleStatus.UNKNOWN
        vulnerability_explanation = "Vulnerability evidence is missing."
    elif service.critical_vulnerabilities == 0:
        vulnerability_status = RuleStatus.PASS
        vulnerability_explanation = "No critical vulnerabilities are reported in this evidence."
    else:
        vulnerability_status = RuleStatus.FAIL
        vulnerability_explanation = "Critical vulnerabilities require review."

    return (
        owner,
        RuleResult(
            rule_id="contract_visible",
            status=contract_status,
            explanation=contract_explanation,
        ),
        RuleResult(
            rule_id="critical_vulnerabilities",
            status=vulnerability_status,
            explanation=vulnerability_explanation,
        ),
    )


def summarize(results: Iterable[RuleResult]) -> ScoreSummary:
    items = tuple(results)
    return ScoreSummary(
        passed=sum(item.status == RuleStatus.PASS for item in items),
        failed=sum(item.status == RuleStatus.FAIL for item in items),
        unknown=sum(item.status == RuleStatus.UNKNOWN for item in items),
        total=len(items),
    )
