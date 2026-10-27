from app.repositories.analytics_repository import (
    AnalyticsFilters,
    AnalyticsRepository,
    GroupAggregate,
)
from app.schemas.analytics import (
    AnalyticsQuery,
    CountryStats,
    DepartmentStats,
    HighestPaidCountry,
    SalaryBand,
    SummaryResponse,
)
from app.schemas.employee import CountryRef, DepartmentRef, EmployeeResponse

# (label, minimum inclusive, maximum exclusive) on annual base salary
SALARY_BANDS: tuple[tuple[str, int, int | None], ...] = (
    ("Under 40k", 0, 40_000),
    ("40k-60k", 40_000, 60_000),
    ("60k-80k", 60_000, 80_000),
    ("80k-100k", 80_000, 100_000),
    ("100k-150k", 100_000, 150_000),
    ("150k+", 150_000, None),
)


def _round(value: float | None) -> float | None:
    return None if value is None else round(value, 2)


def _pay_stats(group: GroupAggregate) -> dict[str, float | int]:
    return {
        "headcount": group.headcount,
        "average_base_salary": round(group.average_base_salary, 2),
        "average_bonus": round(group.average_bonus, 2),
        "total_payroll": group.total_payroll,
    }


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository) -> None:
        self._repository = repository

    def get_summary(self, query: AnalyticsQuery) -> SummaryResponse:
        filters = self._filters(query)
        overall = self._repository.overall(filters)
        country = self._repository.highest_paid_country(filters)

        return SummaryResponse(
            headcount=overall.headcount,
            total_payroll=overall.total_payroll,
            average_base_salary=_round(overall.average_base_salary),
            average_total_compensation=_round(overall.average_total_compensation),
            min_base_salary=overall.min_base_salary,
            max_base_salary=overall.max_base_salary,
            highest_paid_country=(
                None
                if country is None
                else HighestPaidCountry(
                    id=country.id,
                    code=country.code,
                    name=country.name,
                    average_total_compensation=round(
                        country.average_total_compensation, 2
                    ),
                )
            ),
        )

    def get_by_department(self, query: AnalyticsQuery) -> list[DepartmentStats]:
        return [
            DepartmentStats(
                department=DepartmentRef(id=group.id, name=group.name),
                **_pay_stats(group),
            )
            for group in self._repository.by_department(self._filters(query))
        ]

    def get_by_country(self, query: AnalyticsQuery) -> list[CountryStats]:
        return [
            CountryStats(
                country=CountryRef(id=group.id, code=group.code or "", name=group.name),
                **_pay_stats(group),
            )
            for group in self._repository.by_country(self._filters(query))
        ]

    def get_salary_bands(self, query: AnalyticsQuery) -> list[SalaryBand]:
        counts = self._repository.count_by_base_salary_range(
            self._filters(query), [(low, high) for _, low, high in SALARY_BANDS]
        )
        return [
            SalaryBand(label=label, min_salary=low, max_salary=high, headcount=count)
            for (label, low, high), count in zip(SALARY_BANDS, counts, strict=True)
        ]

    def get_top_earners(self, query: AnalyticsQuery, limit: int) -> list[EmployeeResponse]:
        employees = self._repository.top_earners(self._filters(query), limit)
        return [EmployeeResponse.model_validate(e) for e in employees]

    @staticmethod
    def _filters(query: AnalyticsQuery) -> AnalyticsFilters:
        return AnalyticsFilters(
            country_id=query.country_id, department_id=query.department_id
        )
