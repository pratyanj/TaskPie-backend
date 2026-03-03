from sqlmodel import SQLModel, Field
from typing import Optional

class Label(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    color: Optional[str]
    owner_id: int = Field(foreign_key="user.id")
