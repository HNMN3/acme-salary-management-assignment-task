# Testing

## Principles

- **Fast and deterministic.** The backend suite (143 tests) runs in about 2 seconds, the frontend suite (65 tests) in about 10-25 seconds. Nothing sleeps, nothing depends on wall-clock time, and no test asserts latency. Performance is measured separately in [PERFORMANCE.md](PERFORMANCE.md).
- **Isolated.** Every backend test gets its own in-memory SQLite database. Every frontend test stubs `fetch` itself.
- **Small data.** Tests build the few rows they need through factories, so a failure points at one behaviour. The exception is the seed test, which checks the real 10,000-row count.
- **Tests first for the backend.** Each backend feature was committed in two steps: the failing tests, then the implementation.

## Running

| Command | Runs |
|---|---|
| `npm test` | Both suites in Docker |
| `npm run test:backend` | `pytest` in the backend container |
| `npm run test:frontend` | `vitest run` in the frontend container |

Without Docker:

```bash
cd backend && python -m pytest
cd frontend && npm test
```

## Backend

| Area | Location | What it covers |
|---|---|---|
| Models | `tests/unit/test_models.py` | Constraints (positive base salary, non-negative bonus, unique email, unique codes), relationships, timestamps |
| Repositories and services | `tests/unit/` | Pagination, sort order and tie-breaking, search (multi-term, prefix, wildcard escaping, case), filters, salary update rules, analytics values checked against hand-computed numbers, band boundaries |
| HTTP API | `tests/api/` | Status codes, response shape, validation errors (422), unknown employee (404), query-parameter handling for every endpoint |
| Seed | `tests/seed/test_seed.py` | 10,000 employees, determinism for a given random seed, idempotency, `--reset`, realistic pay bounds, pay that differs by country |

Shared fixtures (`tests/conftest.py`):

- `engine` and `db_session`: an in-memory SQLite engine on a static pool, one per test.
- `api_client`: a `TestClient` with the `get_db` dependency overridden to use that session.
- `factories.py`: builders for countries, departments and employees.
- `people.py`: a small named set of four employees reused by the list, search and analytics tests.

## Frontend

Vitest with React Testing Library and `user-event`, in jsdom. Tests sit beside the code they cover.

| Area | What it covers |
|---|---|
| `api/client.test.ts` | Query-string building, PATCH bodies, server error messages, non-JSON error fallback |
| `shared/hooks` | Debounce timing with fake timers; `useAsyncData` loading, errors, reload and stale-response handling |
| `shared/components` | Loading and error states, retry |
| `features/directory` | Rendering, currency formatting, debounced search, sort toggling, filters, reset, pagination, edit modal validation, saving and error display |
| `features/analytics` | Summary cards, chart categories and legends, filters applied to every endpoint, empty states, one failing section isolated from the rest |
| `App.test.tsx` | Backend status badge, tab switching |

Notes:

- jsdom has no layout, so recharts' `ResponsiveContainer` is replaced with a fixed-size wrapper in the analytics tests. They check categories, labels and data, not pixel output.
- Mantine dropdown options render hidden in jsdom, so those lookups use `hidden: true`.
- The `MAX_COMPENSATION` limit (10,000,000) is defined separately in the backend and the frontend. Each side tests its own boundaries.

## Not covered by automated tests

- Pixel-level chart rendering and visual layout.
- Real browser behaviour (the suites run in jsdom).
- Performance (measured by script).
- Concurrent edits (last write wins by design).

## Integration test plan (described, not implemented)

The unit and API tests above use an in-memory database and mocked `fetch`, so nothing proves that the real frontend, backend and database work together. An integration suite would close that gap. It is deliberately left out of this submission.

**Environment.** Start the stack with `docker compose up`, seed 10,000 employees with a fixed random seed, and run the suite against `http://localhost:8000` and `http://localhost:3000`.

**API-level flows** (Python with `httpx`, or Playwright's API client):

1. **Seed integrity.** `GET /employees?page_size=1` reports a total of 10,000. Summary headcount equals the sum of per-department and per-country headcounts.
2. **Edit then read.** `PATCH` a salary, then `GET /employees` and `GET /analytics/summary`. The row, the total payroll and the averages reflect the change.
3. **Filter consistency.** For each country, the list total equals that country's headcount in `/analytics/by-country`.
4. **Pagination.** Walk every page at `page_size=100`. The ids contain no duplicates and no gaps, and the count is 10,000.
5. **Validation round trip.** An out-of-range salary returns 422 and leaves the stored value unchanged.

**Browser flows** (Playwright against the running frontend):

1. **Find and edit.** Search for a known employee, open the edit modal, change base salary and bonus, save, and see the new total in the table.
2. **Filter and sort.** Choose a country and department, sort by total compensation descending, and check that the first row is the maximum for that group.
3. **Dashboard follows filters.** Select a country on the Analytics tab and check that the headcount card matches the directory total for the same country.
4. **Error handling.** Stop the backend container, reload, and check that each section shows an error with a working Retry after restart.

**Data hygiene.** Each run re-seeds with `--reset`, so edits made by one run never affect the next.

**CI.** Run after the unit suites pass, on pull requests only, because it needs Docker and takes minutes rather than seconds.
