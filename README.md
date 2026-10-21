# google-tasks-api

API HTTP (FastAPI) para criar e manipular listas e tarefas do Google Tasks da conta do Manoel.
Projeto independente: ambiente, dependências e segredos ficam só nesta pasta.

## Setup (uma vez)

1. **Google Cloud Console** → criar/selecionar projeto → *APIs & Services*:
   - Ativar a **Google Tasks API**.
   - *OAuth consent screen*: tipo External (ou Internal, se Workspace), adicionar seu e-mail como test user.
   - *Credentials* → *Create credentials* → *OAuth client ID* → **Desktop app** → baixar o JSON.
2. Salvar o JSON como `secrets/credentials.json`.
3. Configurar e autorizar:

```powershell
cd Dev\apis\google-tasks-api
.\.venv\Scripts\Activate.ps1          # se o .venv não existir: py -3.12 -m venv .venv; pip install -r requirements.txt
copy .env.example .env                 # preencher API_KEY
python -m scripts.authorize            # abre o navegador, grava secrets/token.json
```

## Rodar

```powershell
python run.py
```

Docs interativas: http://127.0.0.1:8001/docs (botão *Authorize* → informar a `X-API-Key`).

## Endpoints

| Método | Rota | Ação |
|---|---|---|
| GET/POST | `/tasklists` | listar / criar lista |
| GET/PATCH/DELETE | `/tasklists/{id}` | ver / renomear / excluir lista |
| POST | `/tasklists/{id}/tasks/clear` | ocultar concluídas |
| GET/POST | `/tasklists/{id}/tasks` | listar / criar tarefa (`due` = data `AAAA-MM-DD`, `parent` p/ subtarefa) |
| GET/PATCH/DELETE | `/tasklists/{id}/tasks/{task}` | ver / editar / excluir |
| POST | `/tasklists/{id}/tasks/{task}/complete` | concluir |
| POST | `/tasklists/{id}/tasks/{task}/move` | reordenar, virar subtarefa ou mudar de lista |

Use `@default` como `{id}` para a lista padrão.

## Testes

```powershell
python -m pytest -q
```

## Estrutura

```
app/
  config.py         # settings via .env
  google_client.py  # OAuth + client da Tasks API
  security.py       # X-API-Key
  schemas.py        # modelos de entrada
  routers/          # tasklists.py, tasks.py
scripts/authorize.py
secrets/            # credentials.json, token.json (não versionar)
```

Observação: o Google Tasks guarda só a **data** de vencimento, não a hora.
