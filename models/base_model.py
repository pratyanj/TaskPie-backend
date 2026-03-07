from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class SoftDeleteMixin(SQLModel):
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(default=None, foreign_key="user.id")

class TimestampMixin(SQLModel):
    created_at: datetime = Field(default = datetime.utcnow)
    updated_at: datetime = Field(default = datetime.utcnow)
    created_by: Optional[int] = Field(default=None, foreign_key="user.id")
    updated_by: Optional[int] = Field(default=None, foreign_key="user.id")
