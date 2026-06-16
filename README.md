# Customer Management API

FastAPI backend for the Customer Management API take-home task.

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy async
- asyncpg
- Pydantic v2
- PostgreSQL

Docker is intentionally left for a later pass.

## Local Setup

1. Create and activate a virtual environment.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -e ".[dev]"
```

3. Create `.env`.

```bash
cp .env.example .env
```

4. Start PostgreSQL locally and create the database from `DATABASE_URL`.

```bash
createdb customer_management
```

5. Run the API.

```bash
uvicorn app.main:app --reload
```

The interactive API docs are available at `http://localhost:8000/docs`.

## Endpoints

- `POST /customers`
- `GET /customers`
- `GET /customers/{id}`
- `PUT /customers/{id}`
- `DELETE /customers/{id}`

## Notes

- DAO classes contain database queries only.
- Service classes contain business logic only.
- Credentials are loaded from `.env` and are not hardcoded.

## Common Local PostgreSQL Issue

If startup fails with `role "postgres" does not exist`, your local PostgreSQL install uses
your macOS username as the database role instead of `postgres`. Update `.env` to match your
local role, for example:

```env
DATABASE_URL=postgresql+asyncpg://rahulkoimattur@localhost:5432/customer_management
```

Then create the database as that role:

```bash
createdb customer_management
```
