from sqlalchemy.orm import Session

from app.models import Country, Department, Employee


def make_department(session: Session, name: str = "Engineering") -> Department:
    department = Department(name=name)
    session.add(department)
    session.flush()
    return department


def make_country(
    session: Session, code: str = "US", name: str = "United States"
) -> Country:
    country = Country(code=code, name=name)
    session.add(country)
    session.flush()
    return country


def make_employee(
    session: Session,
    department: Department | None = None,
    country: Country | None = None,
    **overrides: object,
) -> Employee:
    values: dict[str, object] = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "job_title": "Software Engineer",
        "base_salary": 100_000,
        "bonus": 10_000,
        **overrides,
    }
    employee = Employee(
        department=department or make_department(session),
        country=country or make_country(session),
        **values,
    )
    session.add(employee)
    session.flush()
    return employee
