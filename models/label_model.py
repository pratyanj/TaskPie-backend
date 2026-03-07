from sqlmodel import SQLModel, Field
from typing import Optional
from models.base_model import SoftDeleteMixin, TimestampMixin

class Label(SoftDeleteMixin, TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    color: Optional[str]
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
