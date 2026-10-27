# Performance

Measured, not asserted: no test checks timing.

## Method

A script seeded a file-backed SQLite database with the standard 10,000 employees, then ran each operation once to warm up and 30 more times, recording the median and 95th percentile.

- Environment: Windows 11 laptop, Python 3.12.6, SQLite 3.45.3, SQLAlchemy 2.1.6, no Docker.
- Scope: the repository and service layers with a fresh session per call. HTTP routing and JSON serialization are **not** included. Expect a few extra milliseconds per request in the running app.
- Numbers vary by machine. Read them as orders of magnitude.

## Seed

| Operation | Result |
|---|---|
| `seed_database` with 10,000 employees | 0.34 s |

## Latency (median / p95, milliseconds)

| Operation | Median | p95 |
|---|---|---|
| List, page 1, sorted by name | 1.7 | 2.0 |
| List, page 200 (deep), sorted by name | 17.6 | 19.0 |
| List, sorted by total compensation | 5.2 | 5.5 |
| List, sorted by base salary | 5.4 | 5.6 |
| List, filter by country | 2.5 | 2.6 |
| List, filter by country and department | 2.2 | 2.4 |
| List, search `ali` | 7.3 | 8.6 |
| List, search `ali sm` (two terms) | 7.3 | 8.6 |
| List, search by email prefix | 6.9 | 7.5 |
| Analytics summary | 6.3 | 6.6 |
| Analytics by department | 4.3 | 4.6 |
| Analytics by country | 4.3 | 5.1 |
| Analytics salary bands | 4.5 | 5.5 |
| Analytics top earners (10) | 4.6 | 5.5 |

## What the numbers say

- Everything is well under 20 ms, so no screen waits noticeably on the database.
- **Deep pages cost more.** Page 200 is about ten times slower than page 1, because `OFFSET` makes SQLite step over the skipped rows. At 10,000 rows this is irrelevant. Keyset pagination is the fix if it ever matters.
- **Search scans the table.** The plan below shows no index on the search predicate, which is why search costs 7 ms instead of 2 ms. It is still fast at this size.
- **Sorting by salary, bonus or total compensation** uses a temporary B-tree and costs about 5 ms versus 2 ms for the indexed name sort.
- An earlier single cold call through the test client took about 100 ms. That included first-call warm-up (imports, connection, statement compilation) and is not representative.

## Query plans

`EXPLAIN QUERY PLAN` on the statements the repositories actually issue, with the seeded 10,000 rows. Each list request runs a count query and a page query.

Indexes present: `ix_employees_country_id`, `ix_employees_department_id`, `ix_employees_email`, `ix_employees_first_name`, `ix_employees_last_name`.

**List, default (sorted by name)**

```
count:  SCAN employees USING COVERING INDEX ix_employees_department_id
page:   SCAN employees USING INDEX ix_employees_last_name
        SEARCH departments USING INTEGER PRIMARY KEY (rowid=?)
        SEARCH countries USING INTEGER PRIMARY KEY (rowid=?)
        USE TEMP B-TREE FOR RIGHT PART OF ORDER BY
```

The `last_name` index supplies the primary sort. The temporary B-tree covers the remaining sort keys (first name, id).

**List, filtered by country**

```
count:  SEARCH employees USING COVERING INDEX ix_employees_country_id (country_id=?)
page:   SEARCH countries USING INTEGER PRIMARY KEY (rowid=?)
        SEARCH employees USING INDEX ix_employees_country_id (country_id=?)
        SEARCH departments USING INTEGER PRIMARY KEY (rowid=?)
        USE TEMP B-TREE FOR ORDER BY
```

**List, sorted by total compensation**

```
count:  SCAN employees USING COVERING INDEX ix_employees_department_id
page:   SCAN employees USING INDEX ix_employees_department_id
        SEARCH departments USING INTEGER PRIMARY KEY (rowid=?)
        SEARCH countries USING INTEGER PRIMARY KEY (rowid=?)
        USE TEMP B-TREE FOR ORDER BY
```

**List, search `ali`**

```
count:  SCAN employees
page:   SCAN employees USING INDEX ix_employees_last_name
        SEARCH departments USING INTEGER PRIMARY KEY (rowid=?)
        SEARCH countries USING INTEGER PRIMARY KEY (rowid=?)
        USE TEMP B-TREE FOR RIGHT PART OF ORDER BY
```

The count query scans the whole table. SQLite's default `LIKE` is case-insensitive, and a default-collation index cannot serve that, so the prefix pattern does not use `ix_employees_first_name`, `ix_employees_last_name` or `ix_employees_email`.

**Analytics summary**

```
overall:  SCAN employees
country:  SCAN countries
          SEARCH employees USING INDEX ix_employees_country_id (country_id=?)
          USE TEMP B-TREE FOR ORDER BY
```

Aggregates over all rows scan the table once, which is the minimum for an unfiltered aggregate.

## Possible improvements, not done

Not needed at this scale; listed so the reasoning is visible.

1. Make search index-assisted: a `COLLATE NOCASE` index per searched column, or a lowercase search column.
2. Keyset pagination in place of `OFFSET`.
3. A cache for unfiltered analytics, invalidated when a salary is updated.
