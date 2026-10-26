import argparse
import random
from collections import defaultdict
from collections.abc import Sequence

from sqlalchemy import Engine, delete, insert, select
from sqlalchemy.orm import Session

import app.models  # noqa: F401  (registers tables on Base.metadata)
from app.db.base import Base
from app.db.session import get_engine
from app.models import Country, Department, Employee
from seed.data import (
    COUNTRIES,
    DEPARTMENTS,
    FIRST_NAMES,
    LAST_NAMES,
    LEVELS,
    CountrySeed,
    DepartmentSeed,
)

DEFAULT_EMPLOYEE_COUNT = 10_000
DEFAULT_RANDOM_SEED = 42
EMAIL_DOMAIN = "acme.example"
PAY_VARIATION = (0.9, 1.1)
ROUNDING = 500


def _round_pay(amount: float) -> int:
    return int(round(amount / ROUNDING)) * ROUNDING


def _build_employee(
    rng: random.Random,
    department: DepartmentSeed,
    department_id: int,
    country: CountrySeed,
    country_id: int,
    email_counts: defaultdict[str, int],
) -> dict[str, object]:
    first_name = rng.choice(FIRST_NAMES)
    last_name = rng.choice(LAST_NAMES)
    prefix, level_multiplier, _, max_bonus = rng.choices(
        LEVELS, weights=[level[2] for level in LEVELS]
    )[0]
    role = rng.choice(department.roles)

    base_salary = _round_pay(
        department.base_salary
        * level_multiplier
        * country.pay_multiplier
        * rng.uniform(*PAY_VARIATION)
    )
    bonus = _round_pay(base_salary * rng.uniform(0, max_bonus))

    local_part = f"{first_name}.{last_name}".lower()
    email_counts[local_part] += 1
    suffix = "" if email_counts[local_part] == 1 else str(email_counts[local_part])

    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": f"{local_part}{suffix}@{EMAIL_DOMAIN}",
        "job_title": f"{prefix} {role}".strip(),
        "department_id": department_id,
        "country_id": country_id,
        "base_salary": base_salary,
        "bonus": bonus,
    }


def seed_database(
    engine: Engine,
    employee_count: int = DEFAULT_EMPLOYEE_COUNT,
    random_seed: int = DEFAULT_RANDOM_SEED,
    reset: bool = False,
) -> int:
    """Populate the database and return the number of employees inserted."""
    Base.metadata.create_all(engine)
    rng = random.Random(random_seed)

    with Session(engine) as session, session.begin():
        has_employees = session.scalar(select(Employee.id).limit(1)) is not None
        if has_employees and not reset:
            return 0

        session.execute(delete(Employee))
        session.execute(delete(Department))
        session.execute(delete(Country))

        departments = [Department(name=d.name) for d in DEPARTMENTS]
        countries = [Country(code=c.code, name=c.name) for c in COUNTRIES]
        session.add_all([*departments, *countries])
        session.flush()

        email_counts: defaultdict[str, int] = defaultdict(int)
        rows = []
        for _ in range(employee_count):
            department_index = rng.randrange(len(DEPARTMENTS))
            country_index = rng.randrange(len(COUNTRIES))
            rows.append(
                _build_employee(
                    rng,
                    DEPARTMENTS[department_index],
                    departments[department_index].id,
                    COUNTRIES[country_index],
                    countries[country_index].id,
                    email_counts,
                )
            )
        if rows:
            session.execute(insert(Employee), rows)

    return employee_count


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Seed the salary database.")
    parser.add_argument("--count", type=int, default=DEFAULT_EMPLOYEE_COUNT)
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED)
    parser.add_argument("--reset", action="store_true", help="replace existing data")
    args = parser.parse_args(argv)

    inserted = seed_database(get_engine(), args.count, args.seed, args.reset)
    if inserted:
        print(f"Seeded {inserted} employees.")
    else:
        print("Database already seeded; use --reset to replace it.")


if __name__ == "__main__":
    main()
