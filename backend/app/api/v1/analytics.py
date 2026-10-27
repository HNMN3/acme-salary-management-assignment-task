from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import AnalyticsServiceDep
from app.schemas.analytics import (
    AnalyticsQuery,
    CountryStats,
    DepartmentStats,
    SalaryBand,
    SummaryResponse,
    TopEarnersQuery,
)
from app.schemas.employee import EmployeeResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

FilterQuery = Annotated[AnalyticsQuery, Query()]


@router.get("/summary", response_model=SummaryResponse)
def get_summary(query: FilterQuery, service: AnalyticsServiceDep) -> SummaryResponse:
    return service.get_summary(query)


@router.get("/by-department", response_model=list[DepartmentStats])
def get_by_department(
    query: FilterQuery, service: AnalyticsServiceDep
) -> list[DepartmentStats]:
    return service.get_by_department(query)


@router.get("/by-country", response_model=list[CountryStats])
def get_by_country(
    query: FilterQuery, service: AnalyticsServiceDep
) -> list[CountryStats]:
    return service.get_by_country(query)


@router.get("/salary-bands", response_model=list[SalaryBand])
def get_salary_bands(
    query: FilterQuery, service: AnalyticsServiceDep
) -> list[SalaryBand]:
    return service.get_salary_bands(query)


@router.get("/top-earners", response_model=list[EmployeeResponse])
def get_top_earners(
    query: Annotated[TopEarnersQuery, Query()], service: AnalyticsServiceDep
) -> list[EmployeeResponse]:
    return service.get_top_earners(query, query.limit)
