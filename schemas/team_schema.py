from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime


class TeamCreate(SQLModel):
    name: str
    description: Optional[str] = None
    color: str = "#6366F1"
    icon: str = "group"


class TeamUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class TeamMemberRead(SQLModel):
    user_id: int
    email: str
    name: Optional[str]
    role: str
    joined_at: datetime


class TeamRead(SQLModel):
    id: int
    name: str
    description: Optional[str]
    invite_code: str
    color: str
    icon: str
    created_by: int
    created_at: datetime
    member_count: int = 0


class TeamWithMembers(TeamRead):
    members: list[TeamMemberRead] = []


class JoinTeamRequest(SQLModel):
    invite_code: str


class AssignTaskRequest(SQLModel):
    assigned_to: Optional[int] = None  # None = unassign
