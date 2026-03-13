from pydantic import BaseModel
from typing import Optional


class KanbanColumnCreate(BaseModel):
    name: str
    color: Optional[str] = "#6366F1"
    order: Optional[int] = None          # if None, appended to end
    is_done_column: Optional[bool] = False


class KanbanColumnUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    is_done_column: Optional[bool] = None


class KanbanColumnReorder(BaseModel):
    new_order: int


class KanbanColumnRead(BaseModel):
    id: int
    name: str
    color: str
    order: int
    project_id: int
    is_done_column: bool

    class Config:
        from_attributes = True
