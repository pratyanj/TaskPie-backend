from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime

class TaskCreate(SQLModel):
    title: str
    description: Optional[str] = None
    priority: int = 2
    due_date: Optional[datetime] = None
    project_id: Optional[int] = None
    assigned_to: Optional[int] = None
    column_id: Optional[int] = None

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    column_id: Optional[int] = None

class TaskRead(SQLModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    priority: int
    due_date: Optional[datetime] = None
    project_id: Optional[int] = None
    assigned_to: Optional[int] = None
    owner_id: Optional[int] = None
    column_id: Optional[int] = None
    created_at: datetime
