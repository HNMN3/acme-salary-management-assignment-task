from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, ConfigDict
from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.orm import Session, contains_eager, joinedload

from app.models import Country, Department, Employee

EmployeeSortField = Literal[
    "name",
    "job_title",
    "department",
    "country",
    "base_salary",
    "bonus",
    "total_compensation",
]
SortOrder = Literal["asc", "desc"]


class EmployeeListCriteria(BaseModel):
    model_config = ConfigDict(frozen=True)

    page: int = 1
    page_size: int = 50
    sort_by: EmployeeSortField = "name"
    order: SortOrder = "asc"
    search: str | None = None
    country_id: int | None = None
    department_id: int | None = None


def _escape_like(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class EmployeeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_employees(
        self, criteria: EmployeeListCriteria
    ) -> tuple[Sequence[Employee], int]:
        filters = self._filters(criteria)

        total = self._session.scalar(
            select(func.count()).select_from(Employee).where(*filters)
        )

        statement = (
            select(Employee)
            .join(Employee.department)
            .join(Employee.country)
            .options(
                contains_eager(Employee.department),
                contains_eager(Employee.country),
            )
            .where(*filters)
            .order_by(*self._ordering(criteria), Employee.id)
            .limit(criteria.page_size)
            .offset((criteria.page - 1) * criteria.page_size)
        )
        return self._session.scalars(statement).all(), total or 0

    def get_by_id(self, employee_id: int) -> Employee | None:
        statement = (
            select(Employee)
            .options(joinedload(Employee.department), joinedload(Employee.country))
            .where(Employee.id == employee_id)
        )
        return self._session.scalars(statement).first()

    def update_salary(
        self, employee: Employee, base_salary: int, bonus: int
    ) -> Employee:
        employee.base_salary = base_salary
        employee.bonus = bonus
        self._session.commit()
        return employee

    @staticmethod
    def _filters(criteria: EmployeeListCriteria) -> list[ColumnElement[bool]]:
        filters: list[ColumnElement[bool]] = []
        if criteria.country_id is not None:
            filters.append(Employee.country_id == criteria.country_id)
        if criteria.department_id is not None:
            filters.append(Employee.department_id == criteria.department_id)

        for term in (criteria.search or "").split():
            # SQLite LIKE is case-insensitive for ASCII.
            pattern = f"{_escape_like(term)}%"
            filters.append(
                or_(
                    Employee.first_name.like(pattern, escape="\\"),
                    Employee.last_name.like(pattern, escape="\\"),
                    Employee.email.like(pattern, escape="\\"),
                )
            )
        return filters

    @staticmethod
    def _ordering(criteria: EmployeeListCriteria) -> list[ColumnElement]:
        columns: dict[EmployeeSortField, list[ColumnElement]] = {
            "name": [Employee.last_name, Employee.first_name],
            "job_title": [Employee.job_title],
            "department": [Department.name],
            "country": [Country.name],
            "base_salary": [Employee.base_salary],
            "bonus": [Employee.bonus],
            "total_compensation": [Employee.base_salary + Employee.bonus],
        }
        selected = columns[criteria.sort_by]
        if criteria.order == "desc":
            return [column.desc() for column in selected]
        return [column.asc() for column in selected]
