from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class TeamMember(SQLModel, table=True):
    __tablename__ = "team_member"
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="team.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    role: str = Field(default="member")  # "owner" | "admin" | "member"
    joined_at: datetime = Field(default_factory=datetime.utcnow)
