from app.repositories.lookup_repository import LookupRepository
from app.schemas.employee import CountryRef, DepartmentRef
from app.schemas.meta import FilterOptions


class LookupService:
    def __init__(self, repository: LookupRepository) -> None:
        self._repository = repository

    def get_filter_options(self) -> FilterOptions:
        return FilterOptions(
            countries=[
                CountryRef.model_validate(c) for c in self._repository.list_countries()
            ],
            departments=[
                DepartmentRef.model_validate(d)
                for d in self._repository.list_departments()
            ],
        )
