from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, func, inspect, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.session import build_engine
from app.main import create_app
from app.models import Employee

SEED_COUNT = 10_000


@pytest.fixture
def startup_engine(monkeypatch: pytest.MonkeyPatch) -> Iterator[Engine]:
    engine = build_engine("sqlite://")
    monkeypatch.setattr("app.main.get_engine", lambda: engine)
    yield engine
    engine.dispose()


def employee_count(engine: Engine) -> int:
    with Session(engine) as session:
        return session.scalar(select(func.count()).select_from(Employee)) or 0


def test_startup_creates_tables_without_seeding(startup_engine: Engine) -> None:
    with TestClient(create_app(Settings(_env_file=None, seed_on_startup=False))):
        assert inspect(startup_engine).has_table("employees")
        assert employee_count(startup_engine) == 0


def test_startup_seeds_when_enabled(startup_engine: Engine) -> None:
    with TestClient(create_app(Settings(_env_file=None, seed_on_startup=True))):
        assert employee_count(startup_engine) == SEED_COUNT


def test_startup_seeding_is_idempotent(startup_engine: Engine) -> None:
    settings = Settings(_env_file=None, seed_on_startup=True)

    with TestClient(create_app(settings)):
        pass
    with TestClient(create_app(settings)):
        assert employee_count(startup_engine) == SEED_COUNT
