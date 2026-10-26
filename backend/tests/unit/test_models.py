import pytest
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Country, Department, Employee
from tests.factories import make_country, make_department, make_employee


class TestSchema:
    def test_creates_expected_tables(self, engine: Engine) -> None:
        assert {"departments", "countries", "employees"} <= set(
            inspect(engine).get_table_names()
        )

    def test_employee_has_expected_columns(self, engine: Engine) -> None:
        columns = {c["name"] for c in inspect(engine).get_columns("employees")}

        assert columns == {
            "id",
            "first_name",
            "last_name",
            "email",
            "job_title",
            "department_id",
            "country_id",
            "base_salary",
            "bonus",
            "created_at",
            "updated_at",
        }

    @pytest.mark.parametrize(
        "column", ["department_id", "country_id", "last_name", "first_name"]
    )
    def test_employee_column_is_indexed(self, engine: Engine, column: str) -> None:
        indexed = [i["column_names"] for i in inspect(engine).get_indexes("employees")]

        assert [column] in indexed

    def test_employee_email_has_unique_index(self, engine: Engine) -> None:
        indexes = inspect(engine).get_indexes("employees")

        assert any(i["unique"] and i["column_names"] == ["email"] for i in indexes)


class TestEmployee:
    def test_persists_with_related_department_and_country(
        self, db_session: Session
    ) -> None:
        employee = make_employee(
            db_session,
            department=make_department(db_session, "Finance"),
            country=make_country(db_session, "IN", "India"),
        )

        assert employee.id is not None
        assert employee.department.name == "Finance"
        assert employee.country.code == "IN"

    def test_sets_timestamps_on_creation(self, db_session: Session) -> None:
        employee = make_employee(db_session)

        assert employee.created_at is not None
        assert employee.updated_at is not None

    def test_allows_zero_bonus(self, db_session: Session) -> None:
        employee = make_employee(db_session, bonus=0)

        assert employee.bonus == 0

    @pytest.mark.parametrize("base_salary", [0, -1])
    def test_rejects_non_positive_base_salary(
        self, db_session: Session, base_salary: int
    ) -> None:
        with pytest.raises(IntegrityError):
            make_employee(db_session, base_salary=base_salary)

    def test_rejects_negative_bonus(self, db_session: Session) -> None:
        with pytest.raises(IntegrityError):
            make_employee(db_session, bonus=-1)

    def test_rejects_duplicate_email(self, db_session: Session) -> None:
        department = make_department(db_session)
        country = make_country(db_session)
        make_employee(db_session, department, country, email="same@example.com")

        with pytest.raises(IntegrityError):
            make_employee(db_session, department, country, email="same@example.com")

    def test_rejects_unknown_department(self, db_session: Session) -> None:
        country = make_country(db_session)

        with pytest.raises(IntegrityError):
            db_session.add(
                Employee(
                    first_name="Jane",
                    last_name="Doe",
                    email="jane.doe@example.com",
                    job_title="Software Engineer",
                    department_id=999,
                    country_id=country.id,
                    base_salary=100_000,
                    bonus=0,
                )
            )
            db_session.flush()


class TestLookups:
    def test_department_names_are_unique(self, db_session: Session) -> None:
        make_department(db_session, "Engineering")

        with pytest.raises(IntegrityError):
            db_session.add(Department(name="Engineering"))
            db_session.flush()

    def test_country_codes_are_unique(self, db_session: Session) -> None:
        make_country(db_session, "US", "United States")

        with pytest.raises(IntegrityError):
            db_session.add(Country(code="US", name="Another"))
            db_session.flush()
