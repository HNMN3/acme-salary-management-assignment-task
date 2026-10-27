from fastapi import APIRouter

from app.api.deps import LookupServiceDep
from app.schemas.meta import FilterOptions

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/filters", response_model=FilterOptions)
def get_filter_options(service: LookupServiceDep) -> FilterOptions:
    return service.get_filter_options()
