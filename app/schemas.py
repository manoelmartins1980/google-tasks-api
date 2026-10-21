from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class TaskListIn(BaseModel):
    title: str = Field(min_length=1, max_length=1024)


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=1024)
    notes: str | None = None
    due: date | None = Field(None, description="Google Tasks só guarda a data, não a hora.")
    parent: str | None = Field(None, description="ID da tarefa-pai (subtarefa).")
    previous: str | None = Field(None, description="ID da tarefa irmã anterior (ordem).")


class TaskPatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=1024)
    notes: str | None = None
    due: date | None = None
    status: Literal["needsAction", "completed"] | None = None


class TaskMove(BaseModel):
    parent: str | None = None
    previous: str | None = None
    destination_tasklist: str | None = Field(None, description="Mover para outra lista.")


def due_to_rfc3339(d: date) -> str:
    return f"{d.isoformat()}T00:00:00.000Z"
