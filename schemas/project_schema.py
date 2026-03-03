from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime

class ProjectCreate(SQLModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#6366F1"
    icon: Optional[str] = "folder"

class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None

class ProjectRead(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#6366F1"
    icon: Optional[str] = "folder"
    owner_id: int
    created_at: datetime