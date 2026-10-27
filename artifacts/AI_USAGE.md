# AI Usage

This project was built with Claude Code (Anthropic's CLI coding agent) as a pair-programming partner. This note records how it was used, where the human steered it, and what was checked.

## Working agreement

The work was split into 13 checkpoints, each exactly one reviewable commit. After each checkpoint the AI stopped. The author read the diff, ran the tests, committed it, and only then asked for the next one, or asked for fixes first. Where behaviour was testable, tests and implementation were separate checkpoints (`a` writes the failing tests, `b` makes them pass), so no two commits' worth of work was ever pending.

Rules given to the AI at the start:

- Do not name the hiring company anywhere in code, docs or commits.
- Comments only where behaviour is non-obvious, and only about the current state of the code.
- Routers handle HTTP only, services hold business rules, repositories own all SQL.
- Write the requirements document first.

## What the AI did

- Read the brief and critiqued the author's plan before any code was written, listing gaps and trade-offs.
- Drafted the requirements document, execution plan, architecture, performance, testing and AI-usage notes.
- Wrote the backend (models, seed, repositories, services, routers), the frontend (API client, hooks, directory, edit modal, analytics dashboard) and their tests.
- Ran the test suites and a measurement script, and reported the results.

## Decisions the author made

These came from the author, sometimes against the AI's first proposal.

| Decision | Outcome |
|---|---|
| Multi-currency | Questioned where the brief required it. Dropped: single currency (USD), listed as a future enhancement |
| Salary history | Not built; listed as a future enhancement |
| Median | Dropped because SQLite has no median. The author framed this as a design trade-off to document |
| Out-of-scope items | Each must carry a reason, a cost and a revisit trigger in the requirements document |
| Employee create and delete | Confirmed out of scope: the 10,000 seeded employees are the full data set |
| Deployment and demo video | Done by the author manually, kept out of the README |
| Tooling | docker-compose plus root npm scripts; no Makefile |
| Commit discipline | One checkpoint, one commit; tests-first work split into `a` and `b` |
| Data modelling | Asked why dataclasses were used for repository inputs. After the explanation, chose Pydantic models everywhere while keeping the layers |
| Integration tests | Described in `TESTING.md`, deliberately not implemented |

## Prompts that shaped the work

| Stage | Prompt (paraphrased) |
|---|---|
| Kickoff | Understand the brief, give an opinion on my plan, and keep the company name out of the code |
| Plan review | Answer: where does the brief ask for multi-currency or a video or a deployed link? Why block growth beyond 10,000 employees? Keep extras as future enhancements |
| Plan change | Document why SQLite has no median; give every exclusion proper reasoning; follow best practices on where code lives; split tests-first into separate stops |
| Each checkpoint | "Checkpoint N is committed. Start Checkpoint M: ..." |
| Design challenge | "Why did we go with dataclasses instead of pydantic?" then "Keep layers, but use pydantic only" |

## Where the AI was wrong and was corrected

Recorded because they show the review was real.

- **Vacuous tests.** Two salary-update API tests passed before any implementation existed (a 404 check and an "other employees unchanged" check). They were tightened to assert the exact body and a required 200, so they fail without the feature.
- **Seed test bug.** A test used `.tuples()` and failed with `'ChunkedIteratorResult' object is not subscriptable`. It was changed to `.all()` and reported.
- **Overstated search claim.** The requirements said prefix search "stays index-friendly". Measuring with `EXPLAIN QUERY PLAN` showed SQLite's case-insensitive `LIKE` cannot use the default indexes and the query scans the table. The requirements wording was corrected, and `ARCHITECTURE.md` and `PERFORMANCE.md` state the real behaviour and the fix.
- **Misleading timing.** An early 108 ms figure from a single cold call through the test client was not quoted. Steady-state medians over 30 runs are in `PERFORMANCE.md`.
- **Shell and tooling slips.** Some shell heredocs failed on quoting, and a network error interrupted one dependency install. Both were retried. No lasting effect.

## How output was verified

- Every checkpoint ended with the full relevant test suite passing: 154 backend tests and 66 frontend tests at the end of checkpoint 13.
- Analytics tests compare against hand-computed numbers on small fixtures.
- A smoke run against the full 10,000-row seed exercised every endpoint.
- Latency numbers come from a script, not from assertions.
- The author reviewed each diff before committing.

## What was not verified

- Checkpoints 2 to 12 were tested with the local Python and Node toolchains because Docker was not running. At checkpoint 13 the Docker paths were run for the first time: both test suites through `npm test`, `npm run seed`, the development stack and the production stack all worked. A clean `git clone` was not re-run from scratch.
- Charts were tested through a mocked container in jsdom and need a visual check in a real browser.
- Open points kept visible rather than hidden: search scans the table; `updated_at` does not change when a salary is re-submitted with identical values; the repository commits the salary update, so the transaction boundary sits one layer lower than a strict reading of the layering table suggests.
