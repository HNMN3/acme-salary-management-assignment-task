FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

FROM base AS dev

COPY . .
RUN pip install --no-cache-dir -e ".[dev]"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS prod

COPY pyproject.toml ./
COPY app ./app
COPY seed ./seed
RUN pip install --no-cache-dir . \
    && useradd --system --no-create-home app \
    && mkdir /data \
    && chown app /data

ENV DATABASE_URL=sqlite:////data/salary.db

USER app
VOLUME /data
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
