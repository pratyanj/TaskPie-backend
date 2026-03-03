from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str]
    completed: bool = False
    priority: int = Field(default=2)  # 1=High, 2=Medium, 3=Low
    due_date: Optional[datetime]

    owner_id: int = Field(foreign_key="user.id")
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    assigned_to: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskLabel(SQLModel, table=True):
    task_id: int = Field(foreign_key="task.id", primary_key=True)
    label_id: int = Field(foreign_key="label.id", primary_key=True)
    
class TaskAssignee(SQLModel, table=True):
    task_id: int = Field(foreign_key="task.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)