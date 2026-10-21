import json
from unittest.mock import MagicMock

import httplib2
import pytest
from fastapi.testclient import TestClient
from googleapiclient.errors import HttpError

from app.config import settings
from app.google_client import tasks_service
from app.main import app

KEY = "segredo-teste"
client = TestClient(app, headers={"X-API-Key": KEY})
anon = TestClient(app)  # sem chave


@pytest.fixture(autouse=True)
def svc(monkeypatch):
    """Client Google falso, novo a cada teste; API_KEY configurada."""
    mock = MagicMock()
    app.dependency_overrides[tasks_service] = lambda: mock
    monkeypatch.setattr(settings, "api_key", KEY)
    yield mock
    app.dependency_overrides.clear()


def google_error(status: int, message: str) -> HttpError:
    body = json.dumps({"error": {"code": status, "message": message}}).encode()
    return HttpError(httplib2.Response({"status": status}), body)


# --- status ---------------------------------------------------------------


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


# --- listas ---------------------------------------------------------------


def test_list_tasklists_paginates(svc):
    svc.tasklists().list().execute.side_effect = [
        {"items": [{"id": "a"}], "nextPageToken": "p2"},
        {"items": [{"id": "b"}]},
    ]
    assert [t["id"] for t in client.get("/tasklists").json()] == ["a", "b"]
    assert svc.tasklists().list.call_args.kwargs["pageToken"] == "p2"


def test_create_tasklist(svc):
    svc.tasklists().insert().execute.return_value = {"id": "L1", "title": "Casa"}
    r = client.post("/tasklists", json={"title": "Casa"})
    assert r.status_code == 201
    assert r.json()["id"] == "L1"
    assert svc.tasklists().insert.call_args.kwargs["body"] == {"title": "Casa"}


def test_get_tasklist(svc):
    svc.tasklists().get().execute.return_value = {"id": "L1"}
    assert client.get("/tasklists/L1").json() == {"id": "L1"}
    assert svc.tasklists().get.call_args.kwargs == {"tasklist": "L1"}


def test_rename_tasklist(svc):
    svc.tasklists().patch().execute.return_value = {"id": "L1", "title": "Novo"}
    assert client.patch("/tasklists/L1", json={"title": "Novo"}).status_code == 200
    assert svc.tasklists().patch.call_args.kwargs == {"tasklist": "L1", "body": {"title": "Novo"}}


def test_delete_tasklist(svc):
    r = client.delete("/tasklists/L1")
    assert r.status_code == 204
    assert r.content == b""
    assert svc.tasklists().delete.call_args.kwargs == {"tasklist": "L1"}


# --- tarefas --------------------------------------------------------------


def test_list_tasks_passes_filters_and_paginates(svc):
    svc.tasks().list().execute.side_effect = [
        {"items": [{"id": "t1"}], "nextPageToken": "p2"},
        {"items": [{"id": "t2"}]},
    ]
    r = client.get(
        "/tasklists/L1/tasks",
        params={
            "show_completed": "false",
            "show_hidden": "true",
            "due_max": "2026-10-31T00:00:00Z",
        },
    )
    assert [t["id"] for t in r.json()] == ["t1", "t2"]
    kwargs = svc.tasks().list.call_args.kwargs
    assert kwargs["tasklist"] == "L1"
    assert kwargs["showCompleted"] is False
    assert kwargs["showHidden"] is True
    assert kwargs["dueMax"] == "2026-10-31T00:00:00Z"
    assert kwargs["dueMin"] is None


def test_create_task_converts_due_date(svc):
    svc.tasks().insert().execute.return_value = {"id": "t1"}
    r = client.post("/tasklists/L1/tasks", json={"title": "Comprar pão", "due": "2026-10-22"})
    assert r.status_code == 201
    kwargs = svc.tasks().insert.call_args.kwargs
    assert kwargs["body"] == {"title": "Comprar pão", "due": "2026-10-22T00:00:00.000Z"}
    assert kwargs["tasklist"] == "L1"


def test_create_subtask_sends_parent_outside_body(svc):
    client.post("/tasklists/L1/tasks", json={"title": "Sub", "parent": "t1", "previous": "t0"})
    kwargs = svc.tasks().insert.call_args.kwargs
    assert kwargs["parent"] == "t1"
    assert kwargs["previous"] == "t0"
    assert kwargs["body"] == {"title": "Sub"}


def test_get_task(svc):
    svc.tasks().get().execute.return_value = {"id": "t1"}
    assert client.get("/tasklists/L1/tasks/t1").json() == {"id": "t1"}
    assert svc.tasks().get.call_args.kwargs == {"tasklist": "L1", "task": "t1"}


def test_update_task_sends_only_given_fields(svc):
    client.patch("/tasklists/L1/tasks/t1", json={"notes": "obs"})
    assert svc.tasks().patch.call_args.kwargs["body"] == {"notes": "obs"}


def test_reopen_task_clears_completed(svc):
    client.patch("/tasklists/L1/tasks/t1", json={"status": "needsAction"})
    assert svc.tasks().patch.call_args.kwargs["body"] == {
        "status": "needsAction",
        "completed": None,
    }


def test_complete_task(svc):
    svc.tasks().patch().execute.return_value = {"id": "t1", "status": "completed"}
    assert client.post("/tasklists/L1/tasks/t1/complete").json()["status"] == "completed"
    assert svc.tasks().patch.call_args.kwargs == {
        "tasklist": "L1",
        "task": "t1",
        "body": {"status": "completed"},
    }


def test_move_task_to_other_list(svc):
    client.post("/tasklists/L1/tasks/t1/move", json={"destination_tasklist": "L2", "parent": "p"})
    assert svc.tasks().move.call_args.kwargs == {
        "tasklist": "L1",
        "task": "t1",
        "parent": "p",
        "previous": None,
        "destinationTasklist": "L2",
    }


def test_delete_task(svc):
    assert client.delete("/tasklists/L1/tasks/t1").status_code == 204
    assert svc.tasks().delete.call_args.kwargs == {"tasklist": "L1", "task": "t1"}


def test_clear_completed(svc):
    assert client.post("/tasklists/L1/tasks/clear").status_code == 204
    assert svc.tasks().clear.call_args.kwargs == {"tasklist": "L1"}


# --- erros ----------------------------------------------------------------


def test_missing_api_key_returns_401():
    assert anon.get("/tasklists").status_code == 401
    assert anon.get("/tasklists/L1/tasks").status_code == 401


def test_health_is_open_without_key():
    assert anon.get("/health").json() == {"status": "ok"}


def test_wrong_api_key_returns_401():
    assert anon.get("/tasklists", headers={"X-API-Key": "errada"}).status_code == 401


def test_valid_api_key_passes(svc):
    svc.tasklists().list().execute.return_value = {"items": []}
    assert client.get("/tasklists").status_code == 200


def test_unconfigured_api_key_fails_closed(svc, monkeypatch):
    monkeypatch.setattr(settings, "api_key", "")
    r = anon.get("/tasklists")
    assert r.status_code == 503
    assert "API_KEY" in r.json()["detail"]
    svc.tasklists.assert_not_called()


def test_google_404_is_forwarded(svc):
    svc.tasks().get().execute.side_effect = google_error(404, "Task not found.")
    r = client.get("/tasklists/L1/tasks/nao-existe")
    assert r.status_code == 404
    assert r.json() == {"detail": "Task not found."}


def test_google_404_on_tasklist(svc):
    svc.tasklists().delete().execute.side_effect = google_error(404, "Task list not found.")
    assert client.delete("/tasklists/nao-existe").status_code == 404


def test_missing_token_returns_503(svc):
    svc.tasklists().list().execute.side_effect = RuntimeError("Token não encontrado.")
    r = client.get("/tasklists")
    assert r.status_code == 503
    assert "Token" in r.json()["detail"]


@pytest.mark.parametrize("due", ["2026-13-01", "22/10/2026", "amanhã"])
def test_invalid_due_returns_422(svc, due):
    r = client.post("/tasklists/L1/tasks", json={"title": "X", "due": due})
    assert r.status_code == 422
    svc.tasks().insert.assert_not_called()


@pytest.mark.parametrize("body", [{}, {"title": ""}, {"title": "x" * 1025}])
def test_invalid_title_returns_422(body):
    assert client.post("/tasklists", json=body).status_code == 422


def test_invalid_status_returns_422():
    r = client.patch("/tasklists/L1/tasks/t1", json={"status": "done"})
    assert r.status_code == 422
