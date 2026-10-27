# ACME Salary Management

Web application for an HR Manager to browse, search and update the salaries of 10,000 employees across several countries, and to analyse how the organisation pays its people.

- **Directory:** server-side pagination, sorting, debounced prefix search, country and department filters, and a validated salary edit.
- **Analytics:** headcount, payroll and averages, pay by department and country, salary-band distribution and top earners, all filterable.

Stack: FastAPI, SQLAlchemy 2, Pydantic v2, SQLite on the backend; React 19, Vite, TypeScript, Mantine and Recharts on the frontend.

## Prerequisites

- Docker with Compose
- Node.js 20+ (only for the root npm scripts, which wrap Docker Compose)

## Quickstart

```bash
npm run up      # build and start both services (backend :8000, frontend :3000)
npm run seed    # in another terminal: create 10,000 employees
```

Open <http://localhost:3000>. The API docs are at <http://localhost:8000/docs>.

`npm run seed` is safe to repeat: it does nothing if employees already exist. Use `npm run seed -- --reset` to replace the data. The seed is deterministic, so every run produces the same employees.

## Commands

| Command | Purpose |
|---|---|
| `npm run up` | Build and start the development services with live reload |
| `npm run down` | Stop the development services |
| `npm run seed` | Seed 10,000 employees (`-- --reset` replaces existing data, `-- --count N` changes the size) |
| `npm test` | Run the backend and frontend test suites in Docker |
| `npm run test:backend` | Backend tests only |
| `npm run test:frontend` | Frontend tests only |
| `npm run prod:up` | Build and start production images (nginx frontend, non-root backend) in the background |
| `npm run prod:down` | Stop the production services (add `-v` to the underlying command to drop the data volume) |

Without Docker, run `python -m pytest` in `backend/` and `npm test` in `frontend/`.

## Configuration

Copy [.env.example](.env.example) to `.env` to override a default. Docker Compose reads it automatically.

| Variable | Used by | Default | Purpose |
|---|---|---|---|
| `DATABASE_URL` | Backend | `sqlite:///./salary.db` (`sqlite:////data/salary.db` in the production image) | SQLAlchemy database URL |
| `CORS_ORIGINS` | Backend | `http://localhost:3000` | Comma-separated browser origins allowed to call the API |
| `SEED_ON_STARTUP` | Backend | `false` (`true` in `docker-compose.prod.yml`) | Seed 10,000 employees at startup when the database is empty |
| `VITE_API_URL` | Frontend | `http://localhost:8000/api/v1` | API base URL used by the browser. It is compiled into the production build, so rebuild after changing it |

The backend always creates its tables at startup. The production stack keeps the SQLite file on the `salary-data` volume, so data survives restarts.

## Documentation

| Document | Contents |
|---|---|
| [Requirements](artifacts/REQUIREMENTS.md) | Goal, persona, scope, assumptions, and what was deliberately left out and why |
| [Architecture](artifacts/ARCHITECTURE.md) | Layering, API, data model, indexing, search trade-off, future enhancements |
| [Performance](artifacts/PERFORMANCE.md) | Measured latencies and query plans at 10,000 rows |
| [Testing](artifacts/TESTING.md) | Strategy, coverage, and the integration test plan |
| [AI usage](artifacts/AI_USAGE.md) | How AI assistance was used, steered and verified |

## Project layout

```
backend/
  app/        api (routers) -> services -> repositories -> models, plus schemas, core, db
  seed/       deterministic seed data and script
  tests/      unit, api and seed tests
frontend/
  src/api/        typed API client and endpoint functions
  src/features/   directory/ and analytics/, each with its tests
  src/shared/     hooks, components and formatting
artifacts/    project documents
```
