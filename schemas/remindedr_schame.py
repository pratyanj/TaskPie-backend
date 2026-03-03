from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional

class ReminderCreate(SQLModel):
    task_id: int
    remind_at: datetime

class ReminderUpdate(SQLModel):
    remind_at: Optional[datetime] = None
    sent: Optional[bool] = None
