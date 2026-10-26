import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy.orm import Session

from tests.people import People, create_people

EMPLOYEES_URL = "/api/v1/employees"
FILTERS_URL = "/api/v1/meta/filters"


@pytest.fixture
def people(db_session: Session) -> People:
    return create_people(db_session)


def first_names(response: Response) -> list[str]:
    return [item["first_name"] for item in response.json()["items"]]


class TestListEmployees:
    def test_returns_paginated_envelope(
        self, api_client: TestClient, people: People
    ) -> None:
        response = api_client.get(EMPLOYEES_URL, params={"page_size": 2})

        assert response.status_code == 200
        body = response.json()
        assert (body["total"], body["page"], body["page_size"]) == (4, 1, 2)
        assert len(body["items"]) == 2

    def test_defaults_to_page_size_50(
        self, api_client: TestClient, people: People
    ) -> None:
        assert api_client.get(EMPLOYEES_URL).json()["page_size"] == 50

    def test_item_shape(self, api_client: TestClient, people: People) -> None:
        response = api_client.get(EMPLOYEES_URL, params={"search": "alice"})

        assert response.json()["items"] == [
            {
                "id": people.alice.id,
                "first_name": "Alice",
                "last_name": "Zane",
                "email": "alice.zane@acme.example",
                "job_title": "Software Engineer",
                "department": {
                    "id": people.alice.department_id,
                    "name": "Engineering",
                },
                "country": {
                    "id": people.alice.country_id,
                    "code": "US",
                    "name": "United States",
                },
                "base_salary": 100_000,
                "bonus": 10_000,
                "total_compensation": 110_000,
            }
        ]

    def test_pages_through_results(
        self, api_client: TestClient, people: People
    ) -> None:
        response = api_client.get(EMPLOYEES_URL, params={"page": 2, "page_size": 2})

        assert first_names(response) == ["Bob", "Alice"]

    def test_sorts(self, api_client: TestClient, people: People) -> None:
        response = api_client.get(
            EMPLOYEES_URL, params={"sort_by": "total_compensation", "order": "desc"}
        )

        assert first_names(response) == ["Alice", "Alan", "Bob", "Carol"]

    def test_filters_by_country_and_department(
        self, api_client: TestClient, people: People
    ) -> None:
        response = api_client.get(
            EMPLOYEES_URL,
            params={
                "country_id": people.bob.country_id,
                "department_id": people.alice.department_id,
            },
        )

        assert first_names(response) == ["Carol"]
        assert response.json()["total"] == 1

    def test_searches(self, api_client: TestClient, people: People) -> None:
        response = api_client.get(EMPLOYEES_URL, params={"search": "yo"})

        assert first_names(response) == ["Alan", "Bob"]

    @pytest.mark.parametrize(
        "params",
        [
            {"page": 0},
            {"page_size": 0},
            {"page_size": 101},
            {"sort_by": "password"},
            {"order": "sideways"},
            {"country_id": "abc"},
        ],
    )
    def test_rejects_invalid_parameters(
        self, api_client: TestClient, people: People, params: dict[str, object]
    ) -> None:
        assert api_client.get(EMPLOYEES_URL, params=params).status_code == 422


class TestFilterOptions:
    def test_lists_countries_and_departments(
        self, api_client: TestClient, people: People
    ) -> None:
        response = api_client.get(FILTERS_URL)

        assert response.status_code == 200
        body = response.json()
        assert [c["name"] for c in body["countries"]] == ["India", "United States"]
        assert body["countries"][0].keys() == {"id", "code", "name"}
        assert [d["name"] for d in body["departments"]] == ["Engineering", "Finance"]
        assert body["departments"][0].keys() == {"id", "name"}
