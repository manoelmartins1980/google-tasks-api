# Operations

Day-to-day use after the [installation](installation.md).

---

## Running

| Mode | Command | Notes |
|---|---|---|
| **Daily (recommended)** | `.\scripts\install-autostart.ps1` | scheduled task `google-tasks-api` starts at Windows login, no console, restarts up to 3× on failure |
| Manual, no console | `.\.venv\Scripts\pythonw.exe -m scripts.serve` | same as the task |
| Development | `python run.py` | with auto-reload; don't use it as a service |

```powershell
.\scripts\install-autostart.ps1            # install/update and start now
Start-ScheduledTask google-tasks-api       # start / restart
Stop-ScheduledTask google-tasks-api        # stop
Get-ScheduledTask google-tasks-api         # State: Running = up
.\scripts\install-autostart.ps1 -Remove    # uninstall
```

The service takes a few seconds to answer after starting. **After updating the code, restart the task**: it runs without reload.

Why `scripts/serve.py` exists: `pythonw` gives the process no stdout/stderr, and Uvicorn's default logging fails on startup without them. The task registers as `Ready` and nothing listens. `serve.py` redirects both to `logs/api.log`.

## Logs

`logs/api.log` (git-ignored, append-only): startup lines, one access line per request, and errors.

```powershell
Get-Content logs\api.log -Tail 20
Get-Content logs\api.log -Wait          # follow live
```

The file grows with each request. Rotate it by hand when needed: stop the task, rename the file, start the task.

## Using the API

Every data route needs the header `X-API-Key: <API_KEY from .env>`. Examples with `curl.exe` (PowerShell):

```powershell
$H = "X-API-Key: <your key>"
$B = "http://127.0.0.1:8001"

curl.exe -H $H "$B/tasklists"
curl.exe -H $H "$B/tasklists/@default/tasks?show_completed=false"
curl.exe -H $H -H "Content-Type: application/json" -X POST "$B/tasklists/@default/tasks" `
  -d '{\"title\": \"Buy bread\", \"due\": \"2026-10-22\", \"notes\": \"whole grain\"}'
curl.exe -H $H -X POST "$B/tasklists/@default/tasks/<task-id>/complete"
curl.exe -H $H -H "Content-Type: application/json" -X POST "$B/tasklists/<list>/tasks/<task>/move" `
  -d '{\"destination_tasklist\": \"<other-list>\"}'
```

Behaviors worth knowing:
- `due` accepts only a date. The Google Tasks API discards the time.
- Moving a parent task to another list **moves its subtasks too**.
- `PATCH` sends only the fields you include. `{"status": "needsAction"}` reopens a completed task.
- Lists are paginated internally; you always get the full list.

## Status codes

| Code | Meaning | What to do |
|---|---|---|
| `401` | missing or wrong `X-API-Key` | check the header against `.env` |
| `422` | invalid input (e.g. `due` not `YYYY-MM-DD`, empty title) | fix the request; nothing was sent to Google |
| `400` / `404` | forwarded from Google: malformed ID (`400`) or not found (`404`) | check the IDs; the `detail` is Google's message |
| `503` `API_KEY não configurada` | `API_KEY` empty in `.env` | set it and restart |
| `503` `Token não encontrado` / `Token inválido` | no token, or it can't be refreshed | run `python -m scripts.authorize` |

## Token lifecycle

- The access token lasts about 1 hour and is **refreshed automatically** from the refresh token. `secrets/token.json` is rewritten on each refresh.
- **Internal** consent (Workspace): the refresh token keeps working until revoked.
- **External in Testing** (Gmail): the refresh token expires after **7 days**, so re-run `python -m scripts.authorize` weekly.
- Revoke access at <https://myaccount.google.com/permissions>. To re-authorize after revoking, delete `secrets/token.json` and run the authorization again.

## Backup and recovery

Back up these three files, privately (they are secrets):

| File | If lost |
|---|---|
| `.env` | generate a new `API_KEY` and update the clients that use it |
| `secrets/credentials.json` | create a new OAuth client in Google Cloud ([installation §5](installation.md#5-oauth-client)) |
| `secrets/token.json` | run `python -m scripts.authorize` again |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `curl /health` → connection refused | service not running | `Get-ScheduledTask google-tasks-api`; check `logs/api.log`; `Start-ScheduledTask` |
| Task shows `Ready` right after starting, `LastTaskResult` = `1` | started outside `scripts.serve` (no stdout) or crashed on startup | re-run `install-autostart.ps1`; read `logs/api.log` |
| Browser shows `ERR_CONNECTION_REFUSED` with `code=` in the URL | approved after the authorization timed out | run `python -m scripts.authorize` again and approve right away |
| "Google hasn't verified this app" | External consent screen | expected for personal use: **Advanced → Go to ... (unsafe)**. On Workspace, use Internal |
| `403 access_denied` on authorization | account is not a test user (External) or outside the organization (Internal) | add the account as a test user, or use an account of the organization |
| All data routes `503` after a week | External/Testing refresh token expired | `python -m scripts.authorize` |
| Port 8001 in use | another instance (e.g. `run.py` and the task) | stop one; or change `PORT` in `.env` |

## Updating

```powershell
git pull
.\.venv\Scripts\python -m pip install -r requirements.txt
python -m pytest -q
Stop-ScheduledTask google-tasks-api; Start-ScheduledTask google-tasks-api
```
