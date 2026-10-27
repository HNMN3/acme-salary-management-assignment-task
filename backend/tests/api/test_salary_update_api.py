import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.people import People, create_people

EMPLOYEES_URL = "/api/v1/employees"


def salary_url(employee_id: object) -> str:
    return f"{EMPLOYEES_URL}/{employee_id}/salary"


@pytest.fixture
def people(db_session: Session) -> People:
    return create_people(db_session)


def pay_of(api_client: TestClient, first_name: str) -> tuple[int, int]:
    [item] = api_client.get(EMPLOYEES_URL, params={"search": first_name}).json()[
        "items"
    ]
    return item["base_salary"], item["bonus"]


class TestUpdateSalary:
    def test_updates_and_returns_the_employee(
        self, api_client: TestClient, people: People
    ) -> None:
        response = api_client.patch(
            salary_url(people.bob.id), json={"base_salary": 55_000, "bonus": 7_500}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == people.bob.id
        assert body["first_name"] == "Bob"
        assert body["department"]["name"] == "Finance"
        assert body["country"]["code"] == "IN"
        assert body["base_salary"] == 55_000
        assert body["bonus"] == 7_500
        assert body["total_compensation"] == 62_500

    def test_change_is_visible_in_the_list(
        self, api_client: TestClient, people: People
    ) -> None:
        api_client.patch(
            salary_url(people.bob.id), json={"base_salary": 55_000, "bonus": 7_500}
        )

        assert pay_of(api_client, "bob") == (55_000, 7_500)

    def test_does_not_change_other_employees(
        self, api_client: TestClient, people: People
    ) -> None:
        response = api_client.patch(
            salary_url(people.bob.id), json={"base_salary": 55_000, "bonus": 7_500}
        )

        assert response.status_code == 200
        assert pay_of(api_client, "carol") == (50_000, 5_000)

    def test_accepts_zero_bonus(self, api_client: TestClient, people: People) -> None:
        response = api_client.patch(
            salary_url(people.bob.id), json={"base_salary": 55_000, "bonus": 0}
        )

        assert response.status_code == 200
        assert response.json()["total_compensation"] == 55_000

    def test_unknown_employee_returns_404(self, api_client: TestClient) -> None:
        response = api_client.patch(
            salary_url(9999), json={"base_salary": 55_000, "bonus": 0}
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "Employee 9999 not found"}

    def test_non_numeric_id_returns_422(self, api_client: TestClient) -> None:
        response = api_client.patch(
            salary_url("abc"), json={"base_salary": 55_000, "bonus": 0}
        )

        assert response.status_code == 422

    @pytest.mark.parametrize(
        "payload",
        [
            {"base_salary": 0, "bonus": 0},
            {"base_salary": -5, "bonus": 0},
            {"base_salary": 50_000, "bonus": -1},
            {"base_salary": 10_000_001, "bonus": 0},
            {"base_salary": 50_000, "bonus": 10_000_001},
            {"base_salary": 50_000.5, "bonus": 0},
            {"base_salary": "lots", "bonus": 0},
            {"base_salary": 50_000},
            {"bonus": 0},
            {},
        ],
    )
    def test_rejects_invalid_payload_without_changing_data(
        self, api_client: TestClient, people: People, payload: dict[str, object]
    ) -> None:
        response = api_client.patch(salary_url(people.bob.id), json=payload)

        assert response.status_code == 422
        assert pay_of(api_client, "bob") == (40_000, 20_000)
