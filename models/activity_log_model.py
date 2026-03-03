from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class ActivityLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    user_id: int = Field(foreign_key="user.id")      # who performed action
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    
    action: str                                      # e.g., "task_updated"
    details: str                                     # human-readable text
    extra_data: Optional[str] = None                 # JSON field for structured data (old/new values)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
