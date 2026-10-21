# google-tasks-api

Português | **[English](README.md)**

Um pequeno serviço **FastAPI** na frente da **Google Tasks API**: um token OAuth, um lugar só para tratar
erros e uma interface HTTP simples, protegida por uma única chave, para os seus scripts e assistentes.

Feito para uso pessoal numa máquina, com hábitos de produção: falha fechada sem chave, renova o próprio
token, inicia com o Windows sem console e mantém os segredos fora do git.

```
scripts / assistente de IA ──(HTTP + X-API-Key)──> google-tasks-api ──(OAuth)──> Google Tasks API
                                                   127.0.0.1:8001
```

## Endpoints

| Método | Rota | Ação |
|---|---|---|
| GET/POST | `/tasklists` | listar / criar lista |
| GET/PATCH/DELETE | `/tasklists/{id}` | ver / renomear / excluir lista |
| POST | `/tasklists/{id}/tasks/clear` | ocultar concluídas |
| GET/POST | `/tasklists/{id}/tasks` | listar / criar tarefa (`due` = `AAAA-MM-DD`, `parent` para subtarefa) |
| GET/PATCH/DELETE | `/tasklists/{id}/tasks/{task}` | ver / editar / excluir |
| POST | `/tasklists/{id}/tasks/{task}/complete` | concluir |
| POST | `/tasklists/{id}/tasks/{task}/move` | reordenar, virar subtarefa ou mudar de lista |
| GET | `/health` | status (não exige chave) |

Use `@default` como `{id}` para a lista padrão. Docs interativas: `http://127.0.0.1:8001/docs`.

> **Vencimento é só data.** A API do Google Tasks descarta a hora do `due`, mesmo que o app mostre uma,
> então a API só aceita `AAAA-MM-DD` em vez de perder a hora sem avisar.

## Início rápido

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env                 # definir API_KEY
# colocar o cliente OAuth "App para computador" em secrets\credentials.json
python -m scripts.authorize            # abre o navegador, grava secrets\token.json
python run.py                          # desenvolvimento, com reload
```

Guias completos (em inglês):
- **[Instalação](docs/installation.md)**: projeto no Google Cloud, consentimento OAuth (Interno vs Externo), cliente, primeira autorização
- **[Operação](docs/operations.md)**: execução no login, logs, exemplos com `curl`, renovação do token, problemas comuns, backup

## Segurança

- Toda rota de dados exige `X-API-Key`. **Se a `API_KEY` estiver vazia, as rotas de dados respondem `503`**: a API nunca fica aberta por engano.
- Por padrão escuta só em `127.0.0.1`. `/docs` e `/openapi.json` ficam abertos (padrão do FastAPI): proteja ou desative e coloque HTTPS na frente antes de expor na rede.
- `secrets/`, `.env` e `logs/` estão no `.gitignore`.

## Desenvolvimento

```powershell
python -m pytest -q        # 31 testes, client Google simulado
ruff check . ; ruff format --check .
pip-audit -r requirements.txt
```

## Licença

[MIT](LICENSE)
