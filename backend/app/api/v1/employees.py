from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import EmployeeServiceDep
from app.schemas.employee import EmployeeListQuery, PaginatedEmployees

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=PaginatedEmployees)
def list_employees(
    query: Annotated[EmployeeListQuery, Query()],
    service: EmployeeServiceDep,
) -> PaginatedEmployees:
    return service.list_employees(query)
