from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import Settings, settings as default_settings
from app.exceptions import EmployeeNotFoundError


def _employee_not_found_handler(
    _request: Request, error: EmployeeNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(error)}
    )


def create_app(settings: Settings = default_settings) -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(EmployeeNotFoundError, _employee_not_found_handler)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
