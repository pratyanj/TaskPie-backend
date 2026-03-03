from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    google_id: Optional[str] = Field(default=None, unique=True)
    hashed_password: Optional[str] = Field(default=None)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
