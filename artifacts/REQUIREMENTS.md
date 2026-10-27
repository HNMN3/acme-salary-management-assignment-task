# ACME Salary Management - Requirements

## Goal
Replace the spreadsheets ACME's HR team uses to manage salary data for 10,000 employees across multiple countries with a web application that lets the HR Manager find and update an employee's pay and answer questions about how the organisation pays its people.

## Persona
**HR Manager** - a single trusted user who needs to look up individuals, correct their pay, and see the shape of pay across countries and departments. Not a technical user; expects fast, searchable, no-training screens.

## Scope and features

| # | Feature | Why it matters |
|---|---|---|
| 1 | **Employee directory**: server-side paginated table showing name, job title, department, country, base salary, bonus, total compensation | Replaces scrolling a 10,000-row sheet |
| 2 | **Search and filter**: prefix search on name/email; filter by country and department; sort by any column | Finding a person or a group in seconds |
| 3 | **Edit pay**: update an employee's base salary and bonus with validation | The one write operation HR performs |
| 4 | **Pay analytics**: headcount, total payroll, average pay, min/max, highest-paid country; pay by department and by country; salary-band distribution; top earners; filterable by country and department | Answers "how do we pay people?" |
| 5 | **Seed data**: deterministic script producing 10,000 realistic employees | Demonstrates behaviour at the stated scale |

## Assumptions
- All amounts are **annual, whole USD**. Country describes where a person works, not what currency they are paid in.
- Total compensation = base salary + bonus.
- The 10,000 seeded employees are the complete data set; the system manages their pay, not their existence.
- One user; no concurrent-edit conflicts are handled beyond last-write-wins.

## Deliberately left out

| Excluded | Reason | Cost of including it | Revisit when |
|---|---|---|---|
| Authentication and roles | The brief has a single persona and no access-control requirement; a login screen would add no insight into the core problem | Identity, sessions, permission model, tests | Deployed beyond a demo, or a second user type appears |
| Add / delete employees | The brief is about managing *salaries* and analysing pay, not headcount; hiring and exits belong to HR-information systems | Forms, validation, uniqueness rules, delete semantics | HR needs to replace the system of record |
| Salary history / audit trail | Valuable but not asked for; the brief prefers sound judgment over breadth | New table, write-path changes, history UI | Compliance or pay-equity reviews |
| Multi-currency and FX | Needs rates, rate dating and conversion rules that the brief does not mention; one currency keeps every comparison honest | Rate storage, per-employee currency, conversion in every aggregate | Employees must be paid or reported in local currency |
| Median / percentiles | SQLite, chosen for simplicity, has no built-in median; average, min and max already answer the core questions | Application-side calculation or a different database | A pay-equity analysis needs it, or a move to PostgreSQL |
| Payroll execution, tax, payslips | Different product (payments and compliance); the brief is data management and insight | Banking, tax and legal logic per country | Never within this system's remit |
| Employee self-service | The persona is HR only | Second persona, auth, privacy rules | Employees need to view their own pay |
| Import / export | Excel is being replaced, and the seed provides initial data; migration is a one-off | File parsing, validation, error reporting | A real data migration is needed |
| Substring / full-text search | Prefix search keeps matches predictable and is fast at 10,000 rows; infix search matches far more rows and needs a proper index | FTS table and sync logic | The data set outgrows scan performance |

## Success criteria
- Directory pages, filters and search respond quickly with 10,000 rows (measured and reported, not asserted in tests).
- Pay edits are validated (base > 0, bonus >= 0) and reflected immediately.
- Analytics values match hand-computed results in tests.
- Core behaviour is covered by fast, deterministic tests; a clean checkout runs with docker-compose and npm scripts.
