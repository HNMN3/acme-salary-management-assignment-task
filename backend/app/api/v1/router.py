from fastapi import APIRouter

from app.api.v1 import analytics, employees, health, meta

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(analytics.router)
api_router.include_router(employees.router)
api_router.include_router(meta.router)
