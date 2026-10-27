import pytest
from sqlalchemy.orm import Session

from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import AnalyticsQuery
from app.services.analytics_service import AnalyticsService
from tests.factories import make_country, make_department, make_employee
from tests.people import People, create_people


@pytest.fixture
def people(db_session: Session) -> People:
    return create_people(db_session)


@pytest.fixture
def service(db_session: Session) -> AnalyticsService:
    return AnalyticsService(AnalyticsRepository(db_session))


class TestSummary:
    def test_aggregates_the_whole_organisation(
        self, service: AnalyticsService, people: People
    ) -> None:
        summary = service.get_summary(AnalyticsQuery())

        assert summary.headcount == 4
        assert summary.total_payroll == 305_000
        assert summary.average_base_salary == 67_500
        assert summary.average_total_compensation == 76_250
        assert summary.min_base_salary == 40_000
        assert summary.max_base_salary == 100_000

    def test_identifies_highest_paid_country_by_average_total_compensation(
        self, service: AnalyticsService, people: People
    ) -> None:
        country = service.get_summary(AnalyticsQuery()).highest_paid_country

        assert country is not None
        assert country.code == "US"
        assert country.name == "United States"
        assert country.average_total_compensation == 95_000

    def test_respects_country_filter(
        self, service: AnalyticsService, people: People
    ) -> None:
        summary = service.get_summary(AnalyticsQuery(country_id=people.bob.country_id))

        assert summary.headcount == 2
        assert summary.total_payroll == 115_000
        assert summary.average_total_compensation == 57_500
        assert summary.min_base_salary == 40_000
        assert summary.max_base_salary == 50_000
        assert summary.highest_paid_country is not None
        assert summary.highest_paid_country.code == "IN"

    def test_respects_department_filter(
        self, service: AnalyticsService, people: People
    ) -> None:
        summary = service.get_summary(
            AnalyticsQuery(department_id=people.alice.department_id)
        )

        assert summary.headcount == 2
        assert summary.total_payroll == 165_000

    def test_combines_filters(self, service: AnalyticsService, people: People) -> None:
        summary = service.get_summary(
            AnalyticsQuery(
                country_id=people.bob.country_id,
                department_id=people.alice.department_id,
            )
        )

        assert summary.headcount == 1
        assert summary.total_payroll == 55_000

    def test_rounds_averages_to_two_decimals(
        self, service: AnalyticsService, db_session: Session
    ) -> None:
        department, country = make_department(db_session), make_country(db_session)
        for index, base in enumerate([10_000, 10_000, 10_001]):
            make_employee(
                db_session,
                department,
                country,
                email=f"e{index}@acme.example",
                base_salary=base,
                bonus=0,
            )

        assert service.get_summary(AnalyticsQuery()).average_base_salary == 10_000.33

    def test_empty_selection_has_zero_counts_and_no_statistics(
        self, service: AnalyticsService, people: People
    ) -> None:
        summary = service.get_summary(AnalyticsQuery(country_id=9999))

        assert summary.headcount == 0
        assert summary.total_payroll == 0
        assert summary.average_base_salary is None
        assert summary.average_total_compensation is None
        assert summary.min_base_salary is None
        assert summary.max_base_salary is None
        assert summary.highest_paid_country is None


class TestByDepartment:
    def test_groups_pay_by_department_sorted_by_name(
        self, service: AnalyticsService, people: People
    ) -> None:
        rows = service.get_by_department(AnalyticsQuery())

        assert [r.department.name for r in rows] == ["Engineering", "Finance"]
        engineering, finance = rows
        assert engineering.headcount == 2
        assert engineering.average_base_salary == 75_000
        assert engineering.average_bonus == 7_500
        assert engineering.total_payroll == 165_000
        assert finance.headcount == 2
        assert finance.average_base_salary == 60_000
        assert finance.average_bonus == 10_000
        assert finance.total_payroll == 140_000

    def test_respects_country_filter_and_omits_empty_departments(
        self, service: AnalyticsService, people: People
    ) -> None:
        rows = service.get_by_department(
            AnalyticsQuery(country_id=people.alice.country_id)
        )

        assert [(r.department.name, r.headcount) for r in rows] == [
            ("Engineering", 1),
            ("Finance", 1),
        ]
        assert rows[0].total_payroll == 110_000

    def test_empty_selection_returns_no_rows(
        self, service: AnalyticsService, people: People
    ) -> None:
        assert service.get_by_department(AnalyticsQuery(country_id=9999)) == []


class TestByCountry:
    def test_groups_pay_by_country_sorted_by_name(
        self, service: AnalyticsService, people: People
    ) -> None:
        rows = service.get_by_country(AnalyticsQuery())

        assert [r.country.code for r in rows] == ["IN", "US"]
        india, usa = rows
        assert india.headcount == 2
        assert india.average_base_salary == 45_000
        assert india.average_bonus == 12_500
        assert india.total_payroll == 115_000
        assert usa.headcount == 2
        assert usa.average_base_salary == 90_000
        assert usa.average_bonus == 5_000
        assert usa.total_payroll == 190_000

    def test_respects_department_filter(
        self, service: AnalyticsService, people: People
    ) -> None:
        rows = service.get_by_country(
            AnalyticsQuery(department_id=people.alice.department_id)
        )

        assert [(r.country.code, r.total_payroll) for r in rows] == [
            ("IN", 55_000),
            ("US", 110_000),
        ]


class TestSalaryBands:
    def test_counts_headcount_in_every_band_including_empty_ones(
        self, service: AnalyticsService, people: People
    ) -> None:
        bands = service.get_salary_bands(AnalyticsQuery())

        assert [(b.label, b.headcount) for b in bands] == [
            ("Under 40k", 0),
            ("40k-60k", 2),
            ("60k-80k", 0),
            ("80k-100k", 1),
            ("100k-150k", 1),
            ("150k+", 0),
        ]

    def test_band_limits_are_exposed(
        self, service: AnalyticsService, people: People
    ) -> None:
        bands = service.get_salary_bands(AnalyticsQuery())

        assert (bands[0].min_salary, bands[0].max_salary) == (0, 40_000)
        assert (bands[1].min_salary, bands[1].max_salary) == (40_000, 60_000)
        assert (bands[-1].min_salary, bands[-1].max_salary) == (150_000, None)

    def test_lower_bound_is_inclusive_and_upper_bound_exclusive(
        self, service: AnalyticsService, db_session: Session
    ) -> None:
        department, country = make_department(db_session), make_country(db_session)
        for index, base in enumerate([39_999, 40_000, 59_999, 60_000, 150_000]):
            make_employee(
                db_session,
                department,
                country,
                email=f"e{index}@acme.example",
                base_salary=base,
                bonus=0,
            )

        counts = {b.label: b.headcount for b in service.get_salary_bands(AnalyticsQuery())}

        assert counts["Under 40k"] == 1
        assert counts["40k-60k"] == 2
        assert counts["60k-80k"] == 1
        assert counts["150k+"] == 1

    def test_respects_filters(self, service: AnalyticsService, people: People) -> None:
        bands = service.get_salary_bands(AnalyticsQuery(country_id=people.bob.country_id))

        assert {b.label: b.headcount for b in bands}["40k-60k"] == 2
        assert sum(b.headcount for b in bands) == 2


class TestTopEarners:
    def test_orders_by_total_compensation_descending(
        self, service: AnalyticsService, people: People
    ) -> None:
        earners = service.get_top_earners(AnalyticsQuery(), limit=10)

        assert [e.first_name for e in earners] == ["Alice", "Alan", "Bob", "Carol"]
        assert earners[0].total_compensation == 110_000

    def test_honours_limit(self, service: AnalyticsService, people: People) -> None:
        earners = service.get_top_earners(AnalyticsQuery(), limit=2)

        assert [e.first_name for e in earners] == ["Alice", "Alan"]

    def test_respects_filters(self, service: AnalyticsService, people: People) -> None:
        earners = service.get_top_earners(
            AnalyticsQuery(country_id=people.bob.country_id), limit=10
        )

        assert [e.first_name for e in earners] == ["Bob", "Carol"]
