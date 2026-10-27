from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.models import Country, Department, Employee
from tests.factories import make_country, make_department, make_employee


class People(BaseModel):
    """Four employees (creation order = id order) with known, distinct values.

    default name order:       Carol Xu, Alan Young, Bob Young, Alice Zane
    base_salary (asc):        Bob 40k, Carol 50k, Alan 80k, Alice 100k
    total_compensation (asc): Carol 55k, Bob 60k, Alan 80k, Alice 110k
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    alice: Employee
    bob: Employee
    carol: Employee
    alan: Employee


def create_people(session: Session) -> People:
    engineering = make_department(session, "Engineering")
    finance = make_department(session, "Finance")
    usa = make_country(session, "US", "United States")
    india = make_country(session, "IN", "India")

    def person(
        first: str,
        last: str,
        department: Department,
        country: Country,
        base: int,
        bonus: int,
    ) -> Employee:
        return make_employee(
            session,
            department,
            country,
            first_name=first,
            last_name=last,
            email=f"{first}.{last}@acme.example".lower(),
            base_salary=base,
            bonus=bonus,
        )

    return People(
        alice=person("Alice", "Zane", engineering, usa, 100_000, 10_000),
        bob=person("Bob", "Young", finance, india, 40_000, 20_000),
        carol=person("Carol", "Xu", engineering, india, 50_000, 5_000),
        alan=person("Alan", "Young", finance, usa, 80_000, 0),
    )
