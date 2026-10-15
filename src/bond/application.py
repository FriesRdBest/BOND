"""Shared catalog use cases, independent of interface frameworks."""

from bond.domain.models import FrozenModel, RuleResult, ScoreSummary, Service
from bond.domain.rules import evaluate_service, summarize
from bond.repositories.interfaces import CatalogRepository


class ServiceAssessment(FrozenModel):
    service: Service
    results: tuple[RuleResult, ...]
    summary: ScoreSummary


class OrganizationSnapshot(FrozenModel):
    assessments: tuple[ServiceAssessment, ...]
    summary: ScoreSummary

    @property
    def service_count(self) -> int:
        return len(self.assessments)

    @property
    def owned_service_count(self) -> int:
        return sum(assessment.service.owner is not None for assessment in self.assessments)


class CatalogApplication:
    def __init__(self, repository: CatalogRepository) -> None:
        self._repository = repository

    def assess(self, service_id: str) -> ServiceAssessment | None:
        service = self._repository.get_service(service_id)
        if service is None:
            return None
        results = evaluate_service(service)
        return ServiceAssessment(
            service=service,
            results=results,
            summary=summarize(results),
        )

    def snapshot(self) -> OrganizationSnapshot:
        assessments: list[ServiceAssessment] = []
        for service in self._repository.list_services():
            results = evaluate_service(service)
            assessments.append(
                ServiceAssessment(
                    service=service,
                    results=results,
                    summary=summarize(results),
                )
            )
        return OrganizationSnapshot(
            assessments=tuple(assessments),
            summary=summarize(
                result for assessment in assessments for result in assessment.results
            ),
        )
