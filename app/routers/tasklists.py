from fastapi import APIRouter, Depends, Response

from ..google_client import tasks_service
from ..schemas import TaskListIn

router = APIRouter(prefix="/tasklists", tags=["listas"])


@router.get("")
def list_tasklists(svc=Depends(tasks_service)):
    items, token = [], None
    while True:
        res = svc.tasklists().list(maxResults=100, pageToken=token).execute()
        items += res.get("items", [])
        token = res.get("nextPageToken")
        if not token:
            return items


@router.post("", status_code=201)
def create_tasklist(body: TaskListIn, svc=Depends(tasks_service)):
    return svc.tasklists().insert(body=body.model_dump()).execute()


@router.get("/{tasklist_id}")
def get_tasklist(tasklist_id: str, svc=Depends(tasks_service)):
    return svc.tasklists().get(tasklist=tasklist_id).execute()


@router.patch("/{tasklist_id}")
def rename_tasklist(tasklist_id: str, body: TaskListIn, svc=Depends(tasks_service)):
    return svc.tasklists().patch(tasklist=tasklist_id, body=body.model_dump()).execute()


@router.delete("/{tasklist_id}", status_code=204)
def delete_tasklist(tasklist_id: str, svc=Depends(tasks_service)):
    svc.tasklists().delete(tasklist=tasklist_id).execute()
    return Response(status_code=204)
