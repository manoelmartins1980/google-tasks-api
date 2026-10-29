# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [1.0.1] — 2026-10-29

### Changed
- All user-facing text is now in English: error messages (`401`, `503`), the OpenAPI
  description and tags shown in `/docs`, script output, comments and docstrings.
  Clients that matched the old Portuguese `detail` strings must use the new ones
  (see `docs/operations.md`).

## [1.0.0] — 2026-10-21

### Added
- FastAPI service for Google Tasks: CRUD for task lists and tasks, subtasks, complete,
  move (reorder, nest, change list) and hide completed.
- OAuth "Desktop app" flow with automatic token refresh (`scripts/authorize.py`).
- `X-API-Key` authentication on data routes; `GET /health` open for monitoring.
- Console-less daily run on Windows: `scripts/serve.py` (log in `logs/api.log`) and
  `scripts/install-autostart.ps1` (scheduled task at login).
- 31 tests (pytest) with the Google client mocked; lint and formatting with ruff.
- Installation and operations guides in `docs/`; README in English and Portuguese.

### Security
- Fails closed: with no `API_KEY` in `.env`, data routes return `503` instead of running open.
- `secrets/`, `.env` and `logs/` are excluded from version control.
