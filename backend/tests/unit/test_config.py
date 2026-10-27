import pytest

from app.core.config import Settings


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("DATABASE_URL", "CORS_ORIGINS", "SEED_ON_STARTUP"):
        monkeypatch.delenv(name, raising=False)


def build() -> Settings:
    return Settings(_env_file=None)


def test_defaults() -> None:
    settings = build()

    assert settings.database_url == "sqlite:///./salary.db"
    assert settings.cors_origins == ["http://localhost:3000"]
    assert settings.seed_on_startup is False


def test_reads_database_url_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:////data/salary.db")

    assert build().database_url == "sqlite:////data/salary.db"


def test_cors_origins_accepts_a_comma_separated_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "https://a.example, https://b.example ,")

    assert build().cors_origins == ["https://a.example", "https://b.example"]


def test_cors_origins_accepts_a_single_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "https://a.example")

    assert build().cors_origins == ["https://a.example"]


@pytest.mark.parametrize(("raw", "expected"), [("true", True), ("1", True), ("false", False), ("0", False)])
def test_seed_on_startup_parses_booleans(
    monkeypatch: pytest.MonkeyPatch, raw: str, expected: bool
) -> None:
    monkeypatch.setenv("SEED_ON_STARTUP", raw)

    assert build().seed_on_startup is expected
