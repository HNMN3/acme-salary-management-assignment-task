from pydantic import BaseModel

from app.schemas.employee import CountryRef, DepartmentRef


class FilterOptions(BaseModel):
    countries: list[CountryRef]
    departments: list[DepartmentRef]
