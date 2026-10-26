from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


@pytest.fixture
def engine() -> Iterator[Engine]:
    import app.models  # noqa: F401  (registers tables on Base.metadata)
    from app.db.base import Base
    from app.db.session import build_engine

    engine = build_engine("sqlite://")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(engine: Engine) -> Iterator[Session]:
    with Session(engine) as session:
        yield session


@pytest.fixture
def api_client(db_session: Session) -> TestClient:
    from app.db.session import get_db

    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)
