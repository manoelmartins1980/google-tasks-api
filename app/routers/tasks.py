from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel

from ..google_client import tasks_service
from ..schemas import TaskIn, TaskMove, TaskPatch, due_to_rfc3339

router = APIRouter(prefix="/tasklists/{tasklist_id}/tasks", tags=["tasks"])


def _body(model: BaseModel, exclude: frozenset[str] = frozenset()) -> dict:
    data = model.model_dump(exclude_unset=True, exclude=exclude)
    if data.get("due"):
        data["due"] = due_to_rfc3339(data["due"])
    if data.get("status") == "needsAction":
        data["completed"] = None  # reopen the task
    return data


@router.get("")
def list_tasks(
    tasklist_id: str,
    show_completed: bool = True,
    show_hidden: bool = False,
    due_min: str | None = Query(None, description="RFC3339"),
    due_max: str | None = Query(None, description="RFC3339"),
    svc=Depends(tasks_service),
):
    items, token = [], None
    while True:
        res = (
            svc.tasks()
            .list(
                tasklist=tasklist_id,
                maxResults=100,
                pageToken=token,
                showCompleted=show_completed,
                showHidden=show_hidden,
                dueMin=due_min,
                dueMax=due_max,
            )
            .execute()
        )
        items += res.get("items", [])
        token = res.get("nextPageToken")
        if not token:
            return items


@router.post("", status_code=201)
def create_task(tasklist_id: str, body: TaskIn, svc=Depends(tasks_service)):
    return (
        svc.tasks()
        .insert(
            tasklist=tasklist_id,
            parent=body.parent,
            previous=body.previous,
            body=_body(body, exclude={"parent", "previous"}),
        )
        .execute()
    )


@router.get("/{task_id}")
def get_task(tasklist_id: str, task_id: str, svc=Depends(tasks_service)):
    return svc.tasks().get(tasklist=tasklist_id, task=task_id).execute()


@router.patch("/{task_id}")
def update_task(tasklist_id: str, task_id: str, body: TaskPatch, svc=Depends(tasks_service)):
    return svc.tasks().patch(tasklist=tasklist_id, task=task_id, body=_body(body)).execute()


@router.post("/{task_id}/complete")
def complete_task(tasklist_id: str, task_id: str, svc=Depends(tasks_service)):
    return (
        svc.tasks()
        .patch(tasklist=tasklist_id, task=task_id, body={"status": "completed"})
        .execute()
    )


@router.post("/{task_id}/move")
def move_task(tasklist_id: str, task_id: str, body: TaskMove, svc=Depends(tasks_service)):
    return (
        svc.tasks()
        .move(
            tasklist=tasklist_id,
            task=task_id,
            parent=body.parent,
            previous=body.previous,
            destinationTasklist=body.destination_tasklist,
        )
        .execute()
    )


@router.delete("/{task_id}", status_code=204)
def delete_task(tasklist_id: str, task_id: str, svc=Depends(tasks_service)):
    svc.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
    return Response(status_code=204)


@router.post("/clear", status_code=204, tags=["lists"])
def clear_completed(tasklist_id: str, svc=Depends(tasks_service)):
    """Hide all completed tasks in the list."""
    svc.tasks().clear(tasklist=tasklist_id).execute()
    return Response(status_code=204)
