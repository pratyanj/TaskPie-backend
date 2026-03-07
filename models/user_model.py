from sqlmodel import SQLModel, Field
from typing import Optional
from models.base_model import TimestampMixin, SoftDeleteMixin

class User(SoftDeleteMixin, TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    google_id: Optional[str] = Field(default=None, unique=True)
    hashed_password: Optional[str] = Field(default=None)
    name: str
