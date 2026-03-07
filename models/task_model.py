from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from models.base_model import SoftDeleteMixin, TimestampMixin

class Task(SoftDeleteMixin, TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str]
    completed: bool = False
    priority: int = Field(default=2)  # 1=High, 2=Medium, 3=Low
    due_date: Optional[datetime]

    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    assigned_to: Optional[int] = Field(default=None, foreign_key="user.id")
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")


class TaskLabel(SoftDeleteMixin, TimestampMixin, table=True):
    task_id: int = Field(foreign_key="task.id", primary_key=True)
    label_id: int = Field(foreign_key="label.id", primary_key=True)
    
class TaskAssignee(SoftDeleteMixin, TimestampMixin, table=True):
    task_id: int = Field(foreign_key="task.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)