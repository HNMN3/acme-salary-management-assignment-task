from app.repositories.employee_repository import (
    EmployeeListCriteria,
    EmployeeRepository,
)
from app.exceptions import EmployeeNotFoundError
from app.schemas.employee import (
    EmployeeListQuery,
    EmployeeResponse,
    PaginatedEmployees,
    SalaryUpdate,
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

    def update_salary(self, employee_id: int, update: SalaryUpdate) -> EmployeeResponse:
        employee = self._repository.get_by_id(employee_id)
        if employee is None:
            raise EmployeeNotFoundError(employee_id)

        updated = self._repository.update_salary(
            employee, base_salary=update.base_salary, bonus=update.bonus
        )
        return EmployeeResponse.model_validate(updated)
