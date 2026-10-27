from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.exceptions import EmployeeNotFoundError
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import SalaryUpdate
from app.services.employee_service import EmployeeService
from tests.factories import make_employee
from tests.people import People, create_people

LONG_AGO = datetime(2020, 1, 1)


def naive(value: datetime) -> datetime:
    return value.replace(tzinfo=None)


@pytest.fixture
def people(db_session: Session) -> People:
    return create_people(db_session)


class TestEmployeeRepositorySalary:
    def test_get_by_id_returns_employee_with_relations(
        self, db_session: Session, people: People
    ) -> None:
        employee = EmployeeRepository(db_session).get_by_id(people.alice.id)

        assert employee is not None
        assert employee.first_name == "Alice"
        assert employee.department.name == "Engineering"
        assert employee.country.code == "US"

    def test_get_by_id_returns_none_for_unknown_id(self, db_session: Session) -> None:
        assert EmployeeRepository(db_session).get_by_id(9999) is None

    def test_update_salary_changes_base_and_bonus(
        self, db_session: Session, people: People
    ) -> None:
        repository = EmployeeRepository(db_session)

        updated = repository.update_salary(people.bob, base_salary=55_000, bonus=7_500)

        assert (updated.base_salary, updated.bonus) == (55_000, 7_500)

    def test_update_salary_is_committed(
        self, db_session: Session, people: People
    ) -> None:
        employee_id = people.bob.id

        EmployeeRepository(db_session).update_salary(
            people.bob, base_salary=55_000, bonus=7_500
        )
        db_session.rollback()

        reloaded = EmployeeRepository(db_session).get_by_id(employee_id)
        assert reloaded is not None
        assert (reloaded.base_salary, reloaded.bonus) == (55_000, 7_500)

    def test_update_salary_refreshes_updated_at(self, db_session: Session) -> None:
        employee = make_employee(db_session, updated_at=LONG_AGO)

        EmployeeRepository(db_session).update_salary(
            employee, base_salary=120_000, bonus=0
        )
        db_session.refresh(employee)

        assert naive(employee.updated_at) > LONG_AGO

    def test_update_salary_leaves_other_employees_alone(
        self, db_session: Session, people: People
    ) -> None:
        EmployeeRepository(db_session).update_salary(
            people.bob, base_salary=55_000, bonus=7_500
        )

        db_session.refresh(people.carol)
        assert (people.carol.base_salary, people.carol.bonus) == (50_000, 5_000)


class TestEmployeeServiceSalary:
    def test_returns_updated_employee_with_total_compensation(
        self, db_session: Session, people: People
    ) -> None:
        service = EmployeeService(EmployeeRepository(db_session))

        result = service.update_salary(
            people.bob.id, SalaryUpdate(base_salary=55_000, bonus=7_500)
        )

        assert result.id == people.bob.id
        assert result.base_salary == 55_000
        assert result.bonus == 7_500
        assert result.total_compensation == 62_500
        assert result.department.name == "Finance"
        assert result.country.code == "IN"

    def test_does_not_touch_non_salary_fields(
        self, db_session: Session, people: People
    ) -> None:
        service = EmployeeService(EmployeeRepository(db_session))

        result = service.update_salary(
            people.bob.id, SalaryUpdate(base_salary=55_000, bonus=7_500)
        )

        assert (result.first_name, result.last_name) == ("Bob", "Young")
        assert result.email == "bob.young@acme.example"
        assert result.job_title == "Software Engineer"

    def test_unknown_employee_raises_not_found(self, db_session: Session) -> None:
        service = EmployeeService(EmployeeRepository(db_session))

        with pytest.raises(EmployeeNotFoundError):
            service.update_salary(9999, SalaryUpdate(base_salary=55_000, bonus=0))


class TestSalaryUpdateValidation:
    def test_accepts_zero_bonus_and_upper_bounds(self) -> None:
        SalaryUpdate(base_salary=1, bonus=0)
        SalaryUpdate(base_salary=10_000_000, bonus=10_000_000)

    @pytest.mark.parametrize(
        "values",
        [
            {"base_salary": 0, "bonus": 0},
            {"base_salary": -1, "bonus": 0},
            {"base_salary": 50_000, "bonus": -1},
            {"base_salary": 10_000_001, "bonus": 0},
            {"base_salary": 50_000, "bonus": 10_000_001},
            {"base_salary": 50_000.5, "bonus": 0},
        ],
    )
    def test_rejects_invalid_values(self, values: dict[str, object]) -> None:
        with pytest.raises(ValueError):
            SalaryUpdate(**values)
