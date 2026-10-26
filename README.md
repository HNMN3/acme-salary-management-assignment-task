# ACME Salary Management

Web application for an HR Manager to browse, search and update the salaries of 10,000 employees and to analyse how the organisation pays its people.

Requirements: [artifacts/REQUIREMENTS.md](artifacts/REQUIREMENTS.md)

## Prerequisites

- Docker with Compose
- Node.js 20+ (for the root npm scripts)

## Commands

| Command | Purpose |
|---|---|
| `npm run up` | Build and start the services |
| `npm run down` | Stop the services |
| `npm run seed` | Seed 10,000 employees (`npm run seed -- --reset` to replace existing data) |
| `npm test` | Run the test suites |

Full setup, architecture and design notes are added as the project progresses.
