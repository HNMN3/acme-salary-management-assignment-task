from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Country, Department


class LookupRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_countries(self) -> Sequence[Country]:
        return self._session.scalars(select(Country).order_by(Country.name)).all()

    def list_departments(self) -> Sequence[Department]:
        return self._session.scalars(
            select(Department).order_by(Department.name)
        ).all()
