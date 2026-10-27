from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.lookup_repository import LookupRepository
from app.services.analytics_service import AnalyticsService
from app.services.employee_service import EmployeeService
from app.services.lookup_service import LookupService

DbSession = Annotated[Session, Depends(get_db)]


def get_employee_service(session: DbSession) -> EmployeeService:
    return EmployeeService(EmployeeRepository(session))


def get_lookup_service(session: DbSession) -> LookupService:
    return LookupService(LookupRepository(session))


def get_analytics_service(session: DbSession) -> AnalyticsService:
    return AnalyticsService(AnalyticsRepository(session))


AnalyticsServiceDep = Annotated[AnalyticsService, Depends(get_analytics_service)]
EmployeeServiceDep = Annotated[EmployeeService, Depends(get_employee_service)]
LookupServiceDep = Annotated[LookupService, Depends(get_lookup_service)]
