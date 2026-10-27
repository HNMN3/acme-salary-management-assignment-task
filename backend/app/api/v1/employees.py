from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import EmployeeServiceDep
from app.schemas.employee import (
    EmployeeListQuery,
    EmployeeResponse,
    PaginatedEmployees,
    SalaryUpdate,
)

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=PaginatedEmployees)
def list_employees(
    query: Annotated[EmployeeListQuery, Query()],
    service: EmployeeServiceDep,
) -> PaginatedEmployees:
    return service.list_employees(query)


@router.patch("/{employee_id}/salary", response_model=EmployeeResponse)
def update_salary(
    employee_id: int,
    update: SalaryUpdate,
    service: EmployeeServiceDep,
) -> EmployeeResponse:
    return service.update_salary(employee_id, update)
