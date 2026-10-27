from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict
from sqlalchemy import ColumnElement, and_, case, func, select
from sqlalchemy.orm import Session, contains_eager

from app.models import Country, Department, Employee

TOTAL_COMPENSATION = Employee.base_salary + Employee.bonus


class AnalyticsFilters(BaseModel):
    model_config = ConfigDict(frozen=True)

    country_id: int | None = None
    department_id: int | None = None


class OverallStats(BaseModel):
    headcount: int
    total_payroll: int
    average_base_salary: float | None
    average_total_compensation: float | None
    min_base_salary: int | None
    max_base_salary: int | None


class CountryAverage(BaseModel):
    id: int
    code: str
    name: str
    average_total_compensation: float


class GroupAggregate(BaseModel):
    id: int
    name: str
    code: str | None = None
    headcount: int
    average_base_salary: float
    average_bonus: float
    total_payroll: int


class AnalyticsRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def overall(self, filters: AnalyticsFilters) -> OverallStats:
        row = self._session.execute(
            select(
                func.count(Employee.id),
                func.coalesce(func.sum(TOTAL_COMPENSATION), 0),
                func.avg(Employee.base_salary),
                func.avg(TOTAL_COMPENSATION),
                func.min(Employee.base_salary),
                func.max(Employee.base_salary),
            ).where(*self._filters(filters))
        ).one()
        return OverallStats(
            headcount=row[0],
            total_payroll=row[1],
            average_base_salary=row[2],
            average_total_compensation=row[3],
            min_base_salary=row[4],
            max_base_salary=row[5],
        )

    def highest_paid_country(self, filters: AnalyticsFilters) -> CountryAverage | None:
        average = func.avg(TOTAL_COMPENSATION)
        row = self._session.execute(
            select(Country.id, Country.code, Country.name, average)
            .join(Employee, Employee.country_id == Country.id)
            .where(*self._filters(filters))
            .group_by(Country.id)
            .order_by(average.desc(), Country.name)
            .limit(1)
        ).first()
        if row is None:
            return None
        return CountryAverage(
            id=row[0], code=row[1], name=row[2], average_total_compensation=row[3]
        )

    def by_department(self, filters: AnalyticsFilters) -> list[GroupAggregate]:
        statement = (
            select(Department.id, Department.name, *self._group_columns())
            .join(Employee, Employee.department_id == Department.id)
            .where(*self._filters(filters))
            .group_by(Department.id)
            .order_by(Department.name)
        )
        return [
            GroupAggregate(
                id=r[0],
                name=r[1],
                headcount=r[2],
                average_base_salary=r[3],
                average_bonus=r[4],
                total_payroll=r[5],
            )
            for r in self._session.execute(statement)
        ]

    def by_country(self, filters: AnalyticsFilters) -> list[GroupAggregate]:
        statement = (
            select(Country.id, Country.name, Country.code, *self._group_columns())
            .join(Employee, Employee.country_id == Country.id)
            .where(*self._filters(filters))
            .group_by(Country.id)
            .order_by(Country.name)
        )
        return [
            GroupAggregate(
                id=r[0],
                name=r[1],
                code=r[2],
                headcount=r[3],
                average_base_salary=r[4],
                average_bonus=r[5],
                total_payroll=r[6],
            )
            for r in self._session.execute(statement)
        ]

    def count_by_base_salary_range(
        self, filters: AnalyticsFilters, ranges: Sequence[tuple[int, int | None]]
    ) -> list[int]:
        """Headcount per [minimum, maximum) base-salary range; maximum None is open-ended."""
        counts = [
            func.coalesce(
                func.sum(
                    case(
                        (
                            and_(
                                Employee.base_salary >= minimum,
                                *(
                                    [Employee.base_salary < maximum]
                                    if maximum is not None
                                    else []
                                ),
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            )
            for minimum, maximum in ranges
        ]
        row = self._session.execute(select(*counts).where(*self._filters(filters))).one()
        return list(row)

    def top_earners(self, filters: AnalyticsFilters, limit: int) -> Sequence[Employee]:
        statement = (
            select(Employee)
            .join(Employee.department)
            .join(Employee.country)
            .options(
                contains_eager(Employee.department),
                contains_eager(Employee.country),
            )
            .where(*self._filters(filters))
            .order_by(TOTAL_COMPENSATION.desc(), Employee.id)
            .limit(limit)
        )
        return self._session.scalars(statement).all()

    @staticmethod
    def _group_columns() -> tuple[ColumnElement, ...]:
        return (
            func.count(Employee.id),
            func.avg(Employee.base_salary),
            func.avg(Employee.bonus),
            func.sum(TOTAL_COMPENSATION),
        )

    @staticmethod
    def _filters(filters: AnalyticsFilters) -> list[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []
        if filters.country_id is not None:
            conditions.append(Employee.country_id == filters.country_id)
        if filters.department_id is not None:
            conditions.append(Employee.department_id == filters.department_id)
        return conditions
