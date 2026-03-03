from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional

from database import get_session
from models.team_model import Team, generate_invite_code
from models.team_member_model import TeamMember
from models.project_team_model import ProjectTeam
from models.project_model import Project
from models.user_model import User
from models.task_model import Task
from schemas.team_schema import (
    TeamCreate, TeamUpdate, TeamRead, TeamWithMembers,
    TeamMemberRead, JoinTeamRequest, AssignTaskRequest
)
from auth.deps import get_current_user

router = APIRouter(prefix="/teams", tags=["Teams"])


# ─── Helpers ──────────────────────────────────────────────────────────────

def get_team_or_404(team_id: int, session: Session) -> Team:
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


def get_membership_or_403(team_id: int, user_id: int, session: Session) -> TeamMember:
    member = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        )
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="You are not a member of this team")
    return member


def build_team_read(team: Team, session: Session) -> TeamRead:
    count = len(session.exec(
        select(TeamMember).where(TeamMember.team_id == team.id)
    ).all())
    return TeamRead(
        id=team.id,
        name=team.name,
        description=team.description,
        invite_code=team.invite_code,
        color=team.color,
        icon=team.icon,
        created_by=team.created_by,
        created_at=team.created_at,
        member_count=count,
    )


def build_member_read(member: TeamMember, session: Session) -> TeamMemberRead:
    user = session.get(User, member.user_id)
    return TeamMemberRead(
        user_id=member.user_id,
        email=user.email if user else "",
        name=user.name if user else None,
        role=member.role,
        joined_at=member.joined_at,
    )


# ─── Create Team ──────────────────────────────────────────────────────────

@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(
    payload: TeamCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    invite_code = generate_invite_code()
    # Ensure uniqueness
    while session.exec(select(Team).where(Team.invite_code == invite_code)).first():
        invite_code = generate_invite_code()

    team = Team(
        name=payload.name,
        description=payload.description,
        color=payload.color,
        icon=payload.icon,
        invite_code=invite_code,
        created_by=current_user.id,
    )
    session.add(team)
    session.commit()
    session.refresh(team)

    # Auto-join creator as owner
    member = TeamMember(team_id=team.id, user_id=current_user.id, role="owner")
    session.add(member)
    session.commit()

    return build_team_read(team, session)


# ─── List My Teams ─────────────────────────────────────────────────────────

@router.get("/", response_model=list[TeamRead])
def list_my_teams(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    memberships = session.exec(
        select(TeamMember).where(TeamMember.user_id == current_user.id)
    ).all()
    teams = []
    for m in memberships:
        team = session.get(Team, m.team_id)
        if team:
            teams.append(build_team_read(team, session))
    return teams


# ─── Get Team Detail ───────────────────────────────────────────────────────

@router.get("/{team_id}", response_model=TeamWithMembers)
def get_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    team = get_team_or_404(team_id, session)
    get_membership_or_403(team_id, current_user.id, session)

    members_db = session.exec(
        select(TeamMember).where(TeamMember.team_id == team_id)
    ).all()
    members = [build_member_read(m, session) for m in members_db]

    base = build_team_read(team, session)
    return TeamWithMembers(**base.model_dump(), members=members)


# ─── Update Team ───────────────────────────────────────────────────────────

@router.put("/{team_id}", response_model=TeamRead)
def update_team(
    team_id: int,
    payload: TeamUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    team = get_team_or_404(team_id, session)
    membership = get_membership_or_403(team_id, current_user.id, session)

    if membership.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Only owners and admins can update the team")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(team, key, value)

    session.add(team)
    session.commit()
    session.refresh(team)
    return build_team_read(team, session)


# ─── Delete Team ───────────────────────────────────────────────────────────

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    team = get_team_or_404(team_id, session)
    membership = get_membership_or_403(team_id, current_user.id, session)

    if membership.role != "owner":
        raise HTTPException(status_code=403, detail="Only the team owner can delete the team")

    # Cascade-delete members and project links
    members = session.exec(select(TeamMember).where(TeamMember.team_id == team_id)).all()
    for m in members:
        session.delete(m)

    links = session.exec(select(ProjectTeam).where(ProjectTeam.team_id == team_id)).all()
    for link in links:
        session.delete(link)

    session.delete(team)
    session.commit()


# ─── Join Team ─────────────────────────────────────────────────────────────

@router.post("/join", response_model=TeamRead)
def join_team(
    payload: JoinTeamRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    team = session.exec(
        select(Team).where(Team.invite_code == payload.invite_code.strip().upper())
    ).first()
    if not team:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    already = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team.id,
            TeamMember.user_id == current_user.id
        )
    ).first()
    if already:
        raise HTTPException(status_code=400, detail="You are already a member of this team")

    member = TeamMember(team_id=team.id, user_id=current_user.id, role="member")
    session.add(member)
    session.commit()

    return build_team_read(team, session)


# ─── Leave Team ────────────────────────────────────────────────────────────

@router.delete("/{team_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    membership = get_membership_or_403(team_id, current_user.id, session)

    if membership.role == "owner":
        raise HTTPException(
            status_code=400,
            detail="Owner cannot leave. Transfer ownership first or delete the team."
        )

    session.delete(membership)
    session.commit()


# ─── List Members ──────────────────────────────────────────────────────────

@router.get("/{team_id}/members", response_model=list[TeamMemberRead])
def list_members(
    team_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    get_team_or_404(team_id, session)
    get_membership_or_403(team_id, current_user.id, session)

    members_db = session.exec(
        select(TeamMember).where(TeamMember.team_id == team_id)
    ).all()
    return [build_member_read(m, session) for m in members_db]


# ─── Remove a Member ───────────────────────────────────────────────────────

@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    get_team_or_404(team_id, session)
    requester = get_membership_or_403(team_id, current_user.id, session)

    if requester.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Only owners and admins can remove members")

    target = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        )
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Member not found")
    if target.role == "owner":
        raise HTTPException(status_code=400, detail="Cannot remove the team owner")

    session.delete(target)
    session.commit()


# ─── Promote Member to Admin ───────────────────────────────────────────────

@router.patch("/{team_id}/members/{user_id}/promote", response_model=TeamMemberRead)
def promote_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    get_team_or_404(team_id, session)
    requester = get_membership_or_403(team_id, current_user.id, session)

    if requester.role != "owner":
        raise HTTPException(status_code=403, detail="Only the owner can promote members")

    target = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        )
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Member not found")

    target.role = "admin"
    session.add(target)
    session.commit()
    session.refresh(target)
    return build_member_read(target, session)


# ─── Link Project to Team ──────────────────────────────────────────────────

@router.post("/{team_id}/projects/{project_id}", status_code=status.HTTP_201_CREATED)
def link_project(
    team_id: int,
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    get_team_or_404(team_id, session)
    requester = get_membership_or_403(team_id, current_user.id, session)

    if requester.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Only owners and admins can link projects")

    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this project")

    existing = session.exec(
        select(ProjectTeam).where(
            ProjectTeam.team_id == team_id,
            ProjectTeam.project_id == project_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project already linked to this team")

    link = ProjectTeam(team_id=team_id, project_id=project_id)
    session.add(link)
    session.commit()
    return {"message": "Project linked to team"}


# ─── Unlink Project from Team ──────────────────────────────────────────────

@router.delete("/{team_id}/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_project(
    team_id: int,
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    get_team_or_404(team_id, session)
    requester = get_membership_or_403(team_id, current_user.id, session)

    if requester.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Only owners and admins can unlink projects")

    link = session.exec(
        select(ProjectTeam).where(
            ProjectTeam.team_id == team_id,
            ProjectTeam.project_id == project_id
        )
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    session.delete(link)
    session.commit()


# ─── List Team's Projects ──────────────────────────────────────────────────

@router.get("/{team_id}/projects")
def list_team_projects(
    team_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    get_team_or_404(team_id, session)
    get_membership_or_403(team_id, current_user.id, session)

    links = session.exec(
        select(ProjectTeam).where(ProjectTeam.team_id == team_id)
    ).all()
    projects = []
    for link in links:
        project = session.get(Project, link.project_id)
        if project:
            projects.append(project)
    return projects


# ─── Assign Task ───────────────────────────────────────────────────────────

@router.patch("/{team_id}/tasks/{task_id}/assign", response_model=dict)
def assign_task(
    team_id: int,
    task_id: int,
    payload: AssignTaskRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    get_team_or_404(team_id, session)
    get_membership_or_403(team_id, current_user.id, session)

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the task owner can assign it")

    if payload.assigned_to is not None:
        # Verify assignee is in the team
        assignee_member = session.exec(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == payload.assigned_to
            )
        ).first()
        if not assignee_member:
            raise HTTPException(
                status_code=400,
                detail="Assignee must be a member of this team"
            )

    task.assigned_to = payload.assigned_to
    session.add(task)
    session.commit()
    return {"message": "Task assigned", "assigned_to": payload.assigned_to}
