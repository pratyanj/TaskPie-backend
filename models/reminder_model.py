from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from models.base_model import TimestampMixin, SoftDeleteMixin

class Reminder(TimestampMixin, SoftDeleteMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    remind_at: datetime
    sent: bool = False
