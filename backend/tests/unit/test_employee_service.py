import pytest
from sqlalchemy.orm import Session

from app.repositories.employee_repository import EmployeeRepository
from app.repositories.lookup_repository import LookupRepository
from app.schemas.employee import EmployeeListQuery
from app.services.employee_service import EmployeeService
from app.services.lookup_service import LookupService
from tests.people import People, create_people


@pytest.fixture
def people(db_session: Session) -> People:
    return create_people(db_session)


class TestEmployeeService:
    def test_returns_page_metadata_and_total(
        self, db_session: Session, people: People
    ) -> None:
        service = EmployeeService(EmployeeRepository(db_session))

        result = service.list_employees(EmployeeListQuery(page=2, page_size=3))

        assert result.page == 2
        assert result.page_size == 3
        assert result.total == 4
        assert [e.first_name for e in result.items] == ["Alice"]

    def test_item_includes_related_names_and_total_compensation(
        self, db_session: Session, people: People
    ) -> None:
        service = EmployeeService(EmployeeRepository(db_session))

        result = service.list_employees(EmployeeListQuery(search="alice"))

        [alice] = result.items
        assert alice.id == people.alice.id
        assert alice.department.name == "Engineering"
        assert alice.country.code == "US"
        assert alice.base_salary == 100_000
        assert alice.bonus == 10_000
        assert alice.total_compensation == 110_000

    def test_applies_filters_and_sorting(
        self, db_session: Session, people: People
    ) -> None:
        service = EmployeeService(EmployeeRepository(db_session))

        result = service.list_employees(
            EmployeeListQuery(
                country_id=people.bob.country_id,
                sort_by="base_salary",
                order="desc",
            )
        )

        assert [e.first_name for e in result.items] == ["Carol", "Bob"]


class TestLookupService:
    def test_returns_countries_and_departments_sorted_by_name(
        self, db_session: Session, people: People
    ) -> None:
        service = LookupService(LookupRepository(db_session))

        options = service.get_filter_options()

        assert [c.name for c in options.countries] == ["India", "United States"]
        assert [c.code for c in options.countries] == ["IN", "US"]
        assert [d.name for d in options.departments] == ["Engineering", "Finance"]
