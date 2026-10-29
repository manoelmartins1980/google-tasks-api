# Installation

From zero to a working API on Windows. Takes about 20 minutes, most of it in the Google Cloud console.

**Requirements:** Windows 10/11, Python 3.12, a Google account (Workspace or personal Gmail).

---

## 1. Get the code and the environment

```powershell
git clone https://github.com/manoelmartins1980/google-tasks-api.git
cd google-tasks-api
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Create the API key

The key protects every data route. Without it, data routes answer `503`.

```powershell
copy .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Paste the generated value after `API_KEY=` in `.env`. Never commit `.env`; it is git-ignored.

| Variable | Default | Meaning |
|---|---|---|
| `API_KEY` | *(empty → 503)* | value expected in the `X-API-Key` header |
| `HOST` | `127.0.0.1` | bind address; keep it local unless you add HTTPS and protect `/docs` |
| `PORT` | `8001` | port |
| `GOOGLE_CREDENTIALS_FILE` | `secrets/credentials.json` | OAuth client |
| `GOOGLE_TOKEN_FILE` | `secrets/token.json` | token written by the authorization |

## 3. Google Cloud project

At <https://console.cloud.google.com>:

1. **Create a project.** Click the project selector at the top (it shows the current project's name), then **New project**. Name it, e.g. `google-tasks-api`. On Workspace, keep your organization as the location. Make sure the new project is selected afterwards.
2. **Enable the API.** Search for **Google Tasks API** in the top bar and click **Enable**. The API page must show *Status: Enabled*. No billing account is needed.

## 4. OAuth consent screen

Menu **APIs & Services → OAuth consent screen**. Newer consoles call it **Google Auth Platform**. Click **Get started**.

1. **App information:** any name (e.g. `Tasks API personal`) and your support e-mail.
2. **Audience:** this choice matters.

| Your account | Choose | Effect |
|---|---|---|
| Google Workspace (your own domain) | **Internal** | no "unverified app" warning; refresh token without the 7-day limit; no test users needed |
| Personal `@gmail.com` | **External** (leave in *Testing*) | add your address under **Test users**; the refresh token **expires after 7 days**, so you re-run step 6 weekly |

3. **Contact information:** your e-mail. Accept the policy and **Create**.

You don't need to configure scopes. The authorization script requests `https://www.googleapis.com/auth/tasks`.

## 5. OAuth client

**Google Auth Platform → Clients → Create client** (or **Credentials → Create credentials → OAuth client ID**).

1. **Application type: Desktop app.** Not "Web application": the authorization receives the code on a temporary `localhost` port, which only the Desktop type supports without registering redirect URIs.
2. Name it (e.g. `google-tasks-api-local`). Leave *"Use this client for an AI-powered agent"* **unchecked**: the API is the OAuth client, and agents talk to the API with the `X-API-Key`.
3. **Create**, then **Download JSON** right away. Newer consoles may not show the secret again.
4. Save the file as `secrets\credentials.json`.

Google warns that changes can take from 5 minutes to a few hours to apply. If the next step fails right after creating the client, wait and retry.

## 6. First authorization

Have the browser ready, because the local listener waits only a few minutes.

```powershell
python -m scripts.authorize
```

1. The browser opens on Google's sign-in page. If it doesn't, look for a new tab behind other windows.
2. Choose the account whose Tasks you want to manage and click **Allow**.
3. The page shows *"The authentication flow has completed"*, and the console prints `Token saved to ...\secrets\token.json`.

> **`ERR_CONNECTION_REFUSED` on `localhost:<port>/?...&code=...`** means you approved after the script
> had stopped listening. Nothing is broken: run `python -m scripts.authorize` again and approve right away.

## 7. Check it

```powershell
python run.py
```

In another terminal:

```powershell
curl http://127.0.0.1:8001/health
curl -H "X-API-Key: <your key>" http://127.0.0.1:8001/tasklists
```

The first call returns `{"status":"ok"}` and the second returns your task lists. Open `http://127.0.0.1:8001/docs`, click **Authorize**, paste the key, and try the routes.

Next: [Operations](operations.md), to start the API at login, read the logs and troubleshoot.
