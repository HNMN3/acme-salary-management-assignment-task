import pytest
from sqlalchemy.orm import Session

from app.repositories.employee_repository import (
    EmployeeListCriteria,
    EmployeeRepository,
)
from tests.people import People, create_people


@pytest.fixture
def people(db_session: Session) -> People:
    return create_people(db_session)


@pytest.fixture
def repository(db_session: Session, people: People) -> EmployeeRepository:
    return EmployeeRepository(db_session)


def first_names(repository: EmployeeRepository, **criteria: object) -> list[str]:
    employees, _ = repository.list_employees(EmployeeListCriteria(**criteria))
    return [e.first_name for e in employees]


class TestPagination:
    def test_returns_all_employees_and_total(
        self, repository: EmployeeRepository
    ) -> None:
        employees, total = repository.list_employees(EmployeeListCriteria())

        assert len(employees) == 4
        assert total == 4

    def test_returns_requested_page(self, repository: EmployeeRepository) -> None:
        assert first_names(repository, page=1, page_size=2) == ["Carol", "Alan"]
        assert first_names(repository, page=2, page_size=2) == ["Bob", "Alice"]

    def test_page_beyond_the_end_is_empty_but_reports_total(
        self, repository: EmployeeRepository
    ) -> None:
        employees, total = repository.list_employees(
            EmployeeListCriteria(page=3, page_size=2)
        )

        assert employees == []
        assert total == 4

    def test_total_ignores_pagination_but_respects_filters(
        self, repository: EmployeeRepository, people: People
    ) -> None:
        _, total = repository.list_employees(
            EmployeeListCriteria(page_size=1, country_id=people.alice.country_id)
        )

        assert total == 2


class TestSorting:
    def test_defaults_to_last_then_first_name(
        self, repository: EmployeeRepository
    ) -> None:
        assert first_names(repository) == ["Carol", "Alan", "Bob", "Alice"]

    def test_sorts_by_base_salary_descending(
        self, repository: EmployeeRepository
    ) -> None:
        assert first_names(repository, sort_by="base_salary", order="desc") == [
            "Alice",
            "Alan",
            "Carol",
            "Bob",
        ]

    def test_sorts_by_total_compensation_ascending(
        self, repository: EmployeeRepository
    ) -> None:
        assert first_names(repository, sort_by="total_compensation", order="asc") == [
            "Carol",
            "Bob",
            "Alan",
            "Alice",
        ]

    def test_sorts_by_department_name_with_id_tie_break(
        self, repository: EmployeeRepository
    ) -> None:
        assert first_names(repository, sort_by="department") == [
            "Alice",
            "Carol",
            "Bob",
            "Alan",
        ]

    def test_sorts_by_country_name(self, repository: EmployeeRepository) -> None:
        assert first_names(repository, sort_by="country") == [
            "Bob",
            "Carol",
            "Alice",
            "Alan",
        ]


class TestFilters:
    def test_filters_by_country(
        self, repository: EmployeeRepository, people: People
    ) -> None:
        assert first_names(repository, country_id=people.bob.country_id) == [
            "Carol",
            "Bob",
        ]

    def test_filters_by_department(
        self, repository: EmployeeRepository, people: People
    ) -> None:
        assert first_names(repository, department_id=people.alice.department_id) == [
            "Carol",
            "Alice",
        ]

    def test_combines_filters(
        self, repository: EmployeeRepository, people: People
    ) -> None:
        assert first_names(
            repository,
            country_id=people.bob.country_id,
            department_id=people.alice.department_id,
        ) == ["Carol"]

    def test_unknown_filter_value_matches_nothing(
        self, repository: EmployeeRepository
    ) -> None:
        assert first_names(repository, country_id=9999) == []


class TestSearch:
    def test_matches_last_name_prefix_case_insensitively(
        self, repository: EmployeeRepository
    ) -> None:
        assert first_names(repository, search="yo") == ["Alan", "Bob"]
        assert first_names(repository, search="YOUNG") == ["Alan", "Bob"]

    def test_matches_first_name_prefix(self, repository: EmployeeRepository) -> None:
        assert first_names(repository, search="al") == ["Alan", "Alice"]

    def test_matches_email_prefix(self, repository: EmployeeRepository) -> None:
        assert first_names(repository, search="carol.xu@") == ["Carol"]

    def test_every_word_must_match(self, repository: EmployeeRepository) -> None:
        assert first_names(repository, search="alan young") == ["Alan"]
        assert first_names(repository, search="alice young") == []

    def test_does_not_match_in_the_middle_of_a_word(
        self, repository: EmployeeRepository
    ) -> None:
        assert first_names(repository, search="ice") == []

    def test_treats_wildcards_literally(self, repository: EmployeeRepository) -> None:
        assert first_names(repository, search="%") == []
        assert first_names(repository, search="_") == []

    def test_blank_search_is_ignored(self, repository: EmployeeRepository) -> None:
        assert len(first_names(repository, search="   ")) == 4

    def test_combines_with_filters(
        self, repository: EmployeeRepository, people: People
    ) -> None:
        assert first_names(
            repository, search="al", country_id=people.alice.country_id
        ) == ["Alan", "Alice"]
        assert (
            first_names(repository, search="al", country_id=people.bob.country_id)
            == []
        )
