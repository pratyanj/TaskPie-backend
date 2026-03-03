from sqlmodel import SQLModel
from typing import Optional

class LabelCreate(SQLModel):
    name: str
    color: Optional[str] = None

class LabelUpdate(SQLModel):
    name: Optional[str] = None
    color: Optional[str] = None
