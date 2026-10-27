from pydantic import BaseModel, Field

from app.schemas.employee import CountryRef, DepartmentRef


class AnalyticsQuery(BaseModel):
    country_id: int | None = None
    department_id: int | None = None


class TopEarnersQuery(AnalyticsQuery):
    limit: int = Field(10, ge=1, le=100)


class HighestPaidCountry(CountryRef):
    average_total_compensation: float


class SummaryResponse(BaseModel):
    headcount: int
    total_payroll: int
    average_base_salary: float | None
    average_total_compensation: float | None
    min_base_salary: int | None
    max_base_salary: int | None
    highest_paid_country: HighestPaidCountry | None


class PayStats(BaseModel):
    headcount: int
    average_base_salary: float
    average_bonus: float
    total_payroll: int


class DepartmentStats(PayStats):
    department: DepartmentRef


class CountryStats(PayStats):
    country: CountryRef


class SalaryBand(BaseModel):
    label: str
    min_salary: int
    max_salary: int | None
    headcount: int
