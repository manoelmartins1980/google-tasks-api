# google-tasks-api

**[Português](README.pt-BR.md)** | English

A small **FastAPI** service in front of the **Google Tasks API**: one OAuth token, one place to handle
errors, and a plain HTTP interface protected by a single API key for your scripts and assistants.

Built for personal use on one machine, with production habits: fails closed without an API key,
refreshes its own token, starts with Windows without a console, and keeps secrets out of git.

```
scripts / AI assistant ──(HTTP + X-API-Key)──> google-tasks-api ──(OAuth)──> Google Tasks API
                                               127.0.0.1:8001
```

## Endpoints

| Method | Route | Action |
|---|---|---|
| GET/POST | `/tasklists` | list / create task lists |
| GET/PATCH/DELETE | `/tasklists/{id}` | read / rename / delete a list |
| POST | `/tasklists/{id}/tasks/clear` | hide completed tasks |
| GET/POST | `/tasklists/{id}/tasks` | list / create tasks (`due` = `YYYY-MM-DD`, `parent` for subtasks) |
| GET/PATCH/DELETE | `/tasklists/{id}/tasks/{task}` | read / edit / delete |
| POST | `/tasklists/{id}/tasks/{task}/complete` | mark as done |
| POST | `/tasklists/{id}/tasks/{task}/move` | reorder, nest under a parent, or move to another list |
| GET | `/health` | liveness (no key required) |

Use `@default` as `{id}` for the default list. Interactive docs: `http://127.0.0.1:8001/docs`.

> **Due dates are dates.** The Google Tasks API discards the time of `due`, even if the app shows one,
> so the API only accepts `YYYY-MM-DD` instead of silently dropping a time.

## Quick start

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env                 # set API_KEY
# put your OAuth "Desktop app" client in secrets\credentials.json
python -m scripts.authorize            # opens the browser, writes secrets\token.json
python run.py                          # development, with reload
```

Full guides:
- **[Installation](docs/installation.md)**: Google Cloud project, OAuth consent (Internal vs External), client, first authorization
- **[Operations](docs/operations.md)**: running at login, logs, examples with `curl`, token refresh, troubleshooting, backup

## Security

- Every data route requires `X-API-Key`. **If `API_KEY` is empty, data routes return `503`**: the API never runs open by mistake.
- Listens on `127.0.0.1` only by default. `/docs` and `/openapi.json` are open (FastAPI default): protect or disable them and put HTTPS in front before exposing it on a network.
- `secrets/`, `.env` and `logs/` are git-ignored.

## Development

```powershell
python -m pytest -q        # 31 tests, Google client mocked
ruff check . ; ruff format --check .
pip-audit -r requirements.txt
```

## Layout

```
app/
  config.py          # settings from .env
  google_client.py   # OAuth + Tasks API client, token refresh
  security.py        # X-API-Key (fails closed)
  schemas.py         # input models
  routers/           # tasklists.py, tasks.py
scripts/             # authorize.py, serve.py (daily use), install-autostart.ps1
docs/                # installation.md, operations.md
secrets/             # credentials.json, token.json (never committed)
```

## License

[MIT](LICENSE)
