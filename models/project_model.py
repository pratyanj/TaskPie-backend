from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    color: Optional[str] = Field(default="#6366F1")   # Hex accent colour
    icon: Optional[str] = Field(default="folder")      # MaterialIcons name
    owner_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
