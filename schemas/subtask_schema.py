from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SubtaskCreate(BaseModel):
    title: str
    order: Optional[int] = 0


class SubtaskUpdate(BaseModel):
    title: Optional[str] = None


class SubtaskRead(BaseModel):
    id: int
    task_id: int
    title: str
    completed: bool
    order: int
    created_at: datetime
    updated_at: datetime
