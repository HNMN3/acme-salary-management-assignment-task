from app.repositories.employee_repository import (
    EmployeeListCriteria,
    EmployeeRepository,
)
from app.schemas.employee import (
    EmployeeListQuery,
    EmployeeResponse,
    PaginatedEmployees,
)


class EmployeeService:
    def __init__(self, repository: EmployeeRepository) -> None:
        self._repository = repository

    def list_employees(self, query: EmployeeListQuery) -> PaginatedEmployees:
        employees, total = self._repository.list_employees(
            EmployeeListCriteria(**query.model_dump())
        )
        return PaginatedEmployees(
            items=[EmployeeResponse.model_validate(e) for e in employees],
            total=total,
            page=query.page,
            page_size=query.page_size,
        )
