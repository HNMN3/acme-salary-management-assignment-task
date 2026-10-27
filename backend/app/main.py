from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import app.models  # noqa: F401  (registers tables on Base.metadata)
from app.api.v1.router import api_router
from app.core.config import Settings, settings as default_settings
from app.db.base import Base
from app.db.session import get_engine
from app.exceptions import EmployeeNotFoundError
from seed.seed import seed_database


def _employee_not_found_handler(
    _request: Request, error: EmployeeNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(error)}
    )


def create_app(settings: Settings = default_settings) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        engine = get_engine()
        Base.metadata.create_all(engine)
        if settings.seed_on_startup:
            seed_database(engine)
        yield

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
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
