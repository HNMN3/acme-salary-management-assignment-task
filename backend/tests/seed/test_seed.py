from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from app.db.session import build_engine
from app.models import Country, Department, Employee
from seed.data import COUNTRIES, DEPARTMENTS
from seed.seed import seed_database

SMALL_COUNT = 50


def employee_rows(engine: Engine) -> list[tuple]:
    with Session(engine) as session:
        return list(
            session.execute(
                select(
                    Employee.first_name,
                    Employee.last_name,
                    Employee.email,
                    Employee.job_title,
                    Employee.department_id,
                    Employee.country_id,
                    Employee.base_salary,
                    Employee.bonus,
                ).order_by(Employee.id)
            )
        )


def count(session: Session, model: type) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


@pytest.fixture(scope="module")
def full_engine() -> Iterator[Engine]:
    engine = build_engine("sqlite://")
    seed_database(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def small_engine() -> Iterator[Engine]:
    engine = build_engine("sqlite://")
    yield engine
    engine.dispose()


class TestFullSeed:
    def test_creates_exactly_10000_employees(self, full_engine: Engine) -> None:
        with Session(full_engine) as session:
            assert count(session, Employee) == 10_000

    def test_creates_reference_data(self, full_engine: Engine) -> None:
        with Session(full_engine) as session:
            assert count(session, Country) == len(COUNTRIES) == 5
            assert count(session, Department) == len(DEPARTMENTS) == 8

    def test_emails_are_unique_and_well_formed(self, full_engine: Engine) -> None:
        with Session(full_engine) as session:
            emails = session.scalars(select(Employee.email)).all()

        assert len(set(emails)) == len(emails)
        assert all("@" in e and e == e.lower() for e in emails)

    def test_every_country_and_department_has_employees(
        self, full_engine: Engine
    ) -> None:
        with Session(full_engine) as session:
            countries = session.scalars(select(Employee.country_id).distinct()).all()
            departments = session.scalars(
                select(Employee.department_id).distinct()
            ).all()

        assert len(countries) == len(COUNTRIES)
        assert len(departments) == len(DEPARTMENTS)

    def test_pay_differs_by_country(self, full_engine: Engine) -> None:
        with Session(full_engine) as session:
            averages = dict(
                session.execute(
                    select(Country.code, func.avg(Employee.base_salary))
                    .join(Employee, Employee.country_id == Country.id)
                    .group_by(Country.code)
                ).tuples()
            )

        assert averages["US"] > averages["IN"]

    def test_salaries_are_within_realistic_bounds(self, full_engine: Engine) -> None:
        with Session(full_engine) as session:
            low, high = session.execute(
                select(func.min(Employee.base_salary), func.max(Employee.base_salary))
            ).one()

        assert 10_000 <= low
        assert high <= 500_000


class TestSeedBehaviour:
    def test_honours_requested_employee_count(self, small_engine: Engine) -> None:
        seed_database(small_engine, employee_count=SMALL_COUNT)

        with Session(small_engine) as session:
            assert count(session, Employee) == SMALL_COUNT

    def test_same_random_seed_gives_identical_data(self) -> None:
        first, second = build_engine("sqlite://"), build_engine("sqlite://")
        seed_database(first, employee_count=SMALL_COUNT, random_seed=7)
        seed_database(second, employee_count=SMALL_COUNT, random_seed=7)

        assert employee_rows(first) == employee_rows(second)

    def test_different_random_seed_gives_different_data(self) -> None:
        first, second = build_engine("sqlite://"), build_engine("sqlite://")
        seed_database(first, employee_count=SMALL_COUNT, random_seed=1)
        seed_database(second, employee_count=SMALL_COUNT, random_seed=2)

        assert employee_rows(first) != employee_rows(second)

    def test_rerun_does_not_duplicate_data(self, small_engine: Engine) -> None:
        seed_database(small_engine, employee_count=SMALL_COUNT)
        before = employee_rows(small_engine)

        inserted = seed_database(small_engine, employee_count=SMALL_COUNT)

        assert inserted == 0
        assert employee_rows(small_engine) == before

    def test_reset_replaces_existing_data(self, small_engine: Engine) -> None:
        seed_database(small_engine, employee_count=SMALL_COUNT, random_seed=1)

        inserted = seed_database(
            small_engine, employee_count=20, random_seed=2, reset=True
        )

        assert inserted == 20
        with Session(small_engine) as session:
            assert count(session, Employee) == 20
            assert count(session, Country) == len(COUNTRIES)
            assert count(session, Department) == len(DEPARTMENTS)

    def test_returns_number_of_employees_inserted(self, small_engine: Engine) -> None:
        assert seed_database(small_engine, employee_count=SMALL_COUNT) == SMALL_COUNT
