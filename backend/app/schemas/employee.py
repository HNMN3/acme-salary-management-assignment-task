from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.repositories.employee_repository import EmployeeSortField, SortOrder


class EmployeeListQuery(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)
    sort_by: EmployeeSortField = "name"
    order: SortOrder = "asc"
    search: str | None = None
    country_id: int | None = None
    department_id: int | None = None


class DepartmentRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CountryRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str
    job_title: str
    department: DepartmentRef
    country: CountryRef
    base_salary: int
    bonus: int

    @computed_field
    @property
    def total_compensation(self) -> int:
        return self.base_salary + self.bonus


class PaginatedEmployees(BaseModel):
    items: list[EmployeeResponse]
    total: int
    page: int
    page_size: int
