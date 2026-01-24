**Copilot Instructions**

Purpose: Short, actionable guidance to help AI coding agents be productive in this repo.

- **Big Picture**: This project is a hybrid Flask web app (server-rendered UI) with a FastAPI-style router for JSON APIs.
  - Flask app factory: [run.py](run.py) -> `create_app()` in [app/main.py](app/main.py).
  - Flask blueprints live in [app/controllers](app/controllers) and are registered in [app/main.py](app/main.py) (look for `*_bp` names like `vehicle_bp`).
  - FastAPI routers are defined in [app/api/api.py](app/api/api.py) and implemented under [app/api/endpoints](app/api/endpoints).
  - Database: Flask-SQLAlchemy is initialized in [app/extensions.py](app/extensions.py); session helpers in [app/db/session.py].
  - Config: environment-driven config classes in [app/core/config.py] (`DevelopmentConfig`, `ProductionConfig`, `TestingConfig`).

- **Where to change behavior**:
  - Web UI endpoints: add or update a blueprint in [app/controllers] and register it in [app/main.py].
  - JSON APIs: add a router file under [app/api/endpoints] and include it from [app/api/api.py].
  - Business logic: put reusable logic in [app/services] and call it from controllers/endpoints.
  - Models & schema: SQLAlchemy models under [app/models], validation/serialization under [app/schemas].

- **Security & sessions**:
  - Security extensions configured in [app/extensions.py] (Talisman, CSRF, limiter). Respect `app.debug` when toggling HTTPS and cookie flags.
  - CSRF is enforced; tests and templates reference CSRF tokens (see `scripts/check_csrf_templates.py` and tests/test_csrf_*).

- **Database & migrations**:
  - Alembic is present (`alembic.ini`) for migrations. For local/dev the default is SQLite (toggle with `USE_SQLITE` env).
  - DB init scripts live in `archive_root_files/` and `scripts/` (e.g., `init_db.py`, `create_db_tables.py`).

- **Developer workflows / commands** (concrete):
  - Run locally (dev): `python run.py` (uses env vars `HOST`, `PORT`, `DEBUG`).
  - Tests: `python -m pytest` or `pytest -q` (repo contains `pytest.ini`).
  - Migrations: `alembic upgrade head` using `alembic.ini` in repo root.

- **Conventions and patterns to follow**:
  - Controllers (Flask) are thin HTTP layers -> call into services for business rules.
  - Blueprint variables follow `<resource>_bp` and are registered with `url_prefix` in [app/main.py](app/main.py).
  - Use `db.session.get(Model, id)` or `db.session` via `app/extensions.py`'s `db` instance for DB access.
  - Config values come from [app/core/config.py]; prefer environment overrides for secrets and DB credentials.

- **Tests & CI cues**:
  - See `tests/` for integration and unit examples (use TestingConfig which uses in-memory SQLite).
  - Many test files focus on CSRF, reservation flows, and services — copy their fixture patterns when adding new tests.

- **When adding files / PR tips**:
  - Keep controllers minimal and move logic to `app/services` for testability.
  - Register new blueprints in [app/main.py] and include API routers in [app/api/api.py] as appropriate.
  - Run `pytest` after changes and run `alembic` if DB model changes.

If any section is unclear or you want more examples (controller template, service template, or test fixture), say which and I will expand with concrete snippets from the codebase.
