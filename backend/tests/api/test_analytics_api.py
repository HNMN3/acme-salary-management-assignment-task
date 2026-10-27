import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.people import People, create_people

ANALYTICS_URL = "/api/v1/analytics"
ENDPOINTS = [
    "summary",
    "by-department",
    "by-country",
    "salary-bands",
    "top-earners",
]


@pytest.fixture
def people(db_session: Session) -> People:
    return create_people(db_session)


class TestSummary:
    def test_returns_organisation_summary(
        self, api_client: TestClient, people: People
    ) -> None:
        response = api_client.get(f"{ANALYTICS_URL}/summary")

        assert response.status_code == 200
        assert response.json() == {
            "headcount": 4,
            "total_payroll": 305_000,
            "average_base_salary": 67_500,
            "average_total_compensation": 76_250,
            "min_base_salary": 40_000,
            "max_base_salary": 100_000,
            "highest_paid_country": {
                "id": people.alice.country_id,
                "code": "US",
                "name": "United States",
                "average_total_compensation": 95_000,
            },
        }

    def test_applies_filters(self, api_client: TestClient, people: People) -> None:
        response = api_client.get(
            f"{ANALYTICS_URL}/summary",
            params={
                "country_id": people.bob.country_id,
                "department_id": people.alice.department_id,
            },
        )

        assert response.json()["headcount"] == 1
        assert response.json()["total_payroll"] == 55_000

    def test_empty_selection(self, api_client: TestClient, people: People) -> None:
        response = api_client.get(f"{ANALYTICS_URL}/summary", params={"country_id": 9999})

        assert response.status_code == 200
        assert response.json() == {
            "headcount": 0,
            "total_payroll": 0,
            "average_base_salary": None,
            "average_total_compensation": None,
            "min_base_salary": None,
            "max_base_salary": None,
            "highest_paid_country": None,
        }


class TestGroupedEndpoints:
    def test_by_department(self, api_client: TestClient, people: People) -> None:
        response = api_client.get(f"{ANALYTICS_URL}/by-department")

        assert response.status_code == 200
        assert response.json()[0] == {
            "department": {"id": people.alice.department_id, "name": "Engineering"},
            "headcount": 2,
            "average_base_salary": 75_000,
            "average_bonus": 7_500,
            "total_payroll": 165_000,
        }
        assert [r["department"]["name"] for r in response.json()] == [
            "Engineering",
            "Finance",
        ]

    def test_by_country(self, api_client: TestClient, people: People) -> None:
        response = api_client.get(f"{ANALYTICS_URL}/by-country")

        assert response.status_code == 200
        assert response.json()[0] == {
            "country": {"id": people.bob.country_id, "code": "IN", "name": "India"},
            "headcount": 2,
            "average_base_salary": 45_000,
            "average_bonus": 12_500,
            "total_payroll": 115_000,
        }

    def test_grouped_endpoints_apply_filters(
        self, api_client: TestClient, people: People
    ) -> None:
        response = api_client.get(
            f"{ANALYTICS_URL}/by-country",
            params={"department_id": people.alice.department_id},
        )

        assert [(r["country"]["code"], r["total_payroll"]) for r in response.json()] == [
            ("IN", 55_000),
            ("US", 110_000),
        ]


class TestSalaryBands:
    def test_returns_all_bands_in_order(
        self, api_client: TestClient, people: People
    ) -> None:
        response = api_client.get(f"{ANALYTICS_URL}/salary-bands")

        assert response.status_code == 200
        assert response.json() == [
            {"label": "Under 40k", "min_salary": 0, "max_salary": 40_000, "headcount": 0},
            {"label": "40k-60k", "min_salary": 40_000, "max_salary": 60_000, "headcount": 2},
            {"label": "60k-80k", "min_salary": 60_000, "max_salary": 80_000, "headcount": 0},
            {"label": "80k-100k", "min_salary": 80_000, "max_salary": 100_000, "headcount": 1},
            {"label": "100k-150k", "min_salary": 100_000, "max_salary": 150_000, "headcount": 1},
            {"label": "150k+", "min_salary": 150_000, "max_salary": None, "headcount": 0},
        ]


class TestTopEarners:
    def test_returns_employees_ordered_by_total_compensation(
        self, api_client: TestClient, people: People
    ) -> None:
        response = api_client.get(f"{ANALYTICS_URL}/top-earners", params={"limit": 3})

        assert response.status_code == 200
        body = response.json()
        assert [e["first_name"] for e in body] == ["Alice", "Alan", "Bob"]
        assert body[0]["total_compensation"] == 110_000
        assert body[0]["department"]["name"] == "Engineering"

    def test_defaults_to_ten(self, api_client: TestClient, people: People) -> None:
        assert len(api_client.get(f"{ANALYTICS_URL}/top-earners").json()) == 4

    def test_applies_filters(self, api_client: TestClient, people: People) -> None:
        response = api_client.get(
            f"{ANALYTICS_URL}/top-earners",
            params={"country_id": people.bob.country_id},
        )

        assert [e["first_name"] for e in response.json()] == ["Bob", "Carol"]

    @pytest.mark.parametrize("limit", [0, 101, "abc"])
    def test_rejects_invalid_limit(
        self, api_client: TestClient, people: People, limit: object
    ) -> None:
        response = api_client.get(f"{ANALYTICS_URL}/top-earners", params={"limit": limit})

        assert response.status_code == 422


class TestFilterValidation:
    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    @pytest.mark.parametrize("param", ["country_id", "department_id"])
    def test_rejects_non_numeric_filters(
        self, api_client: TestClient, endpoint: str, param: str
    ) -> None:
        response = api_client.get(f"{ANALYTICS_URL}/{endpoint}", params={param: "abc"})

        assert response.status_code == 422
