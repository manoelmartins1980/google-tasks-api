import json

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from googleapiclient.errors import HttpError

from .routers import tasklists, tasks
from .security import require_api_key

app = FastAPI(
    title="Google Tasks API",
    version="0.1.0",
    description="Criação e manipulação de listas e tarefas do Google Tasks.",
)
# X-API-Key só nas rotas de dados; /health fica aberto para monitoramento.
app.include_router(tasklists.router, dependencies=[Depends(require_api_key)])
app.include_router(tasks.router, dependencies=[Depends(require_api_key)])


@app.exception_handler(HttpError)
async def google_error(_: Request, exc: HttpError):
    try:
        detail = json.loads(exc.content).get("error", {}).get("message", str(exc))
    except ValueError:
        detail = str(exc)
    return JSONResponse(status_code=exc.resp.status, content={"detail": detail})


@app.exception_handler(RuntimeError)
async def auth_error(_: Request, exc: RuntimeError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.get("/health", tags=["status"])
def health():
    return {"status": "ok"}
