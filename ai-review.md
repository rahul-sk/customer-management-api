# AI Code Review

Review requested: entire codebase for correctness, layer separation, security issues, and Python quality.

Scope reviewed:
- FastAPI routes
- Pydantic schemas
- SQLAlchemy async model and database setup
- DAO, service, validator, and factory layers
- Dockerfile and docker-compose.yml
- README and environment examples

Checks run:
- `python3 -X pycache_prefix=.pycache -m compileall app` - passed
- `.venv/bin/ruff check .` - passed

## Summary

The codebase is in good shape for an initial take-home implementation. It follows the required stack, keeps DAO and service responsibilities mostly separate, uses async SQLAlchemy correctly at a basic level, and avoids hardcoded application credentials in source code. The refactors to move customer construction into a factory, email checks into a validator, and soft-delete state mutation onto the entity improve the single-responsibility story.

The main issues to address before final submission are around update validation and transaction error handling. There are also a couple of production-readiness improvements worth considering, especially migrations and Docker verification.

## Findings

### P1 - Nullable update fields can violate required database columns

File: `app/schemas/customer.py`
Lines: 24-32

`CustomerUpdate` defines required fields such as `first_name`, `last_name`, `email`, `date_of_birth`, `account_status`, and `credit_score` as nullable. Because `CustomerFactory.apply_update()` applies any explicitly provided field, a client can send values like:

```json
{
  "first_name": null
}
```

That passes request validation but later violates the database `nullable=False` constraint. In `CustomerService.update_customer()`, the resulting `IntegrityError` is currently converted to `DuplicateEmailError`, producing a misleading 409 conflict for a non-email validation problem.

Recommended fix:
- For fields that may be omitted but cannot be set to null, avoid `str | None` style request types for required database columns, or add Pydantic validators that reject explicit nulls.
- Keep nullable types only for fields that are actually nullable, such as `phone_number` and `address`.
- Do not map every `IntegrityError` to duplicate email.

### P2 - `IntegrityError` handling assumes every database constraint failure is duplicate email

File: `app/services/customer_service.py`
Lines: 25-30 and 51-56

Both create and update catch any `IntegrityError` and raise `DuplicateEmailError`. This is reasonable as a fallback for a unique email race condition, but it is too broad. Other database failures, such as null constraint violations or enum issues, would be returned as "A customer with this email already exists."

Recommended fix:
- Either inspect the PostgreSQL/asyncpg exception details before mapping to duplicate email, or introduce a generic persistence exception for unexpected integrity failures.
- Ideally validate request data before persistence so database constraint errors are rare and meaningful.

### P2 - Delete path does not rollback if commit fails

File: `app/services/customer_service.py`
Lines: 60-64

`delete_customer()` mutates the entity, saves it, and commits, but unlike create/update it does not wrap the transaction in `try/except` with rollback. If flush or commit fails, the session may remain in a failed state for the request lifecycle.

Recommended fix:
- Add the same transaction handling shape used by create/update.
- Longer term, consider a small Unit of Work abstraction so transaction handling is consistent across use cases.

### P2 - Application creates tables at startup instead of using migrations

File: `app/main.py`
Lines: 14-17

`create_database_tables()` is convenient for an interview scaffold, but automatic schema creation at app startup is not ideal for production or collaborative development. It can hide schema drift and does not support controlled migrations.

Recommended fix:
- Keep this for the take-home if simplicity matters.
- For a stronger submission, add Alembic migrations and replace startup table creation with documented migration commands.

### P3 - Docker setup could not be executed in this environment

Files: `Dockerfile`, `docker-compose.yml`

The Dockerfile and Compose file match the PRD direction: multi-stage build, slim base image, non-root runtime user, API plus PostgreSQL, healthcheck dependency, environment injection, and persistent database volume. However, Docker was not installed in the current environment, so the image build and Compose startup were not actually verified here.

Recommended fix:
- Run `docker compose config`.
- Run `docker compose up --build`.
- Verify `GET /health` and at least one full customer create/list request through the Dockerized API.

### P3 - No automated API tests yet

Files: `tests/`

The project has test tooling configured, but there are no tests. Manual Swagger/curl validation is useful, but automated tests would strengthen confidence and interview quality.

Recommended fix:
- Add unit tests for `CustomerValidator` and `CustomerFactory`.
- Add service tests with a mocked DAO/session.
- Add integration tests later with a test PostgreSQL container.

## Layer Separation Review

DAO layer:
- `CustomerDAO` is now persistence-focused: save, list, get by id, get by email.
- It no longer performs soft-delete state mutation, which is good for SRP.

Service layer:
- `CustomerService` coordinates use cases and transactions.
- Business checks are delegated to `CustomerValidator`.
- Entity construction and update mapping are delegated to `CustomerFactory`.
- Remaining improvement: centralize transaction management so service methods do not repeat commit/rollback patterns.

Model layer:
- `Customer` owns its `mark_deleted()` state transition.
- Field definitions match the PRD.

Schema layer:
- Pydantic v2 models are used appropriately.
- Main issue: update schema permits explicit nulls for required fields.

Route layer:
- Routes are thin and call service methods.
- HTTP exception mapping is clear, though global exception handlers could reduce repeated try/except blocks.

## Security Review

Positive:
- `.env` is ignored by Git.
- `.dockerignore` excludes `.env`, `.venv`, `.git`, caches, and local artifacts.
- Docker runtime uses a non-root user.
- SQLAlchemy parameterized query construction avoids raw SQL injection risks.
- DB connection and statement timeouts are configurable.

Risks / improvements:
- `.env.example` contains development credentials. This is acceptable for local examples, but real credentials must never be committed.
- `DEBUG=true` in `.env.example` is convenient locally but should be false outside local development.
- No authentication/authorization is present. The PRD does not require it, but it should be noted if this were a real customer API.

## Python Quality Review

Positive:
- Type hints are used throughout.
- Pydantic models avoid bare dict passing between layers.
- Async database access uses `AsyncSession` and `async_sessionmaker`.
- Custom exceptions are defined and propagated meaningfully at route boundaries.
- Ruff passes.

Improvements:
- Avoid broad `IntegrityError` translation to duplicate email.
- Add tests before final submission.
- Consider global FastAPI exception handlers for custom application exceptions.
- Consider Alembic for schema migrations.

## Recommended Next Actions

1. Fix `CustomerUpdate` so explicit nulls cannot be sent for required fields.
2. Narrow `IntegrityError` handling or introduce a generic persistence error.
3. Add rollback handling to `delete_customer()`.
4. Run Docker locally and verify the Compose flow.
5. Add a small focused test suite.

## Final Assessment

The implementation is a solid initial version and aligns well with the PRD's architectural expectations. The DAO/service separation is defensible, the code is readable, and Docker support has been added with the right major pieces. Before submission, I would address the update validation and transaction-handling findings, then run a Docker smoke test and add at least a few tests.
