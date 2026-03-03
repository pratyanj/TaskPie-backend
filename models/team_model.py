from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import secrets
import string


def generate_invite_code() -> str:
    """Generate a unique 8-char invite code like TEAM-XK92."""
    chars = string.ascii_uppercase + string.digits
    code = ''.join(secrets.choice(chars) for _ in range(8))
    return f"TEAM-{code[:4]}"


class Team(SQLModel, table=True):
    __tablename__ = "team"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    invite_code: str = Field(unique=True, index=True)
    color: str = Field(default="#6366F1")
    icon: str = Field(default="group")
    created_by: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
