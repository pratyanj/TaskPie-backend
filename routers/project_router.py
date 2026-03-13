from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models.project_model import Project
from schemas.project_schema import ProjectCreate, ProjectUpdate, ProjectRead
from auth.deps import get_current_user
from models.user_model import User
from models.project_team_model import ProjectTeam
from models.team_model import Team
from models.team_member_model import TeamMember
from schemas.team_schema import TeamRead, TeamMemberRead
from routers.kanban_router import create_default_columns

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=ProjectRead)
def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    db_project = Project(**project.dict(), owner_id=current_user.id)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    # Auto-create 4 default Kanban columns for the new project
    create_default_columns(db_project.id, session)
    return db_project


@router.get("/", response_model=list[ProjectRead])
def get_projects(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return session.exec(select(Project).where(Project.owner_id == current_user.id)).all()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    project = session.exec(select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    project = session.exec(select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in project_update.dict(exclude_unset=True).items():
        setattr(project, key, value)
    
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    project = session.exec(select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    session.delete(project)
    session.commit()
    return {"message": "Project deleted successfully"}


@router.get("/{project_id}/teams", response_model=list[TeamRead])
def get_project_teams(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all teams this project is linked to."""
    # Ensure user has access to project
    project = session.exec(select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    links = session.exec(select(ProjectTeam).where(ProjectTeam.project_id == project_id)).all()
    teams = []
    for link in links:
        team = session.get(Team, link.team_id)
        if team:
            count = len(session.exec(
                select(TeamMember).where(TeamMember.team_id == team.id)
            ).all())
            teams.append(TeamRead(
                id=team.id,
                name=team.name,
                description=team.description,
                invite_code=team.invite_code,
                color=team.color,
                icon=team.icon,
                created_by=team.created_by,
                created_at=team.created_at,
                member_count=count
            ))
            
    return teams

@router.get("/{project_id}/members", response_model=list[TeamMemberRead])
def get_project_members(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all unique members from all teams this project is linked to."""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    has_access = False
    if project.owner_id == current_user.id:
        has_access = True
        
    links = session.exec(select(ProjectTeam).where(ProjectTeam.project_id == project_id)).all()
    
    unique_members = {}
    for link in links:
        members = session.exec(select(TeamMember).where(TeamMember.team_id == link.team_id)).all()
        for m in members:
            if m.user_id == current_user.id:
                has_access = True
                
            if m.user_id not in unique_members:
                user = session.get(User, m.user_id)
                if user:
                    unique_members[m.user_id] = TeamMemberRead(
                        user_id=m.user_id,
                        email=user.email if user else "",
                        name=user.name if user else None,
                        role=m.role,
                        joined_at=m.joined_at,
                    )
                    
    if not has_access:
        raise HTTPException(status_code=403, detail="Not authorized to view members")
                  
    return list(unique_members.values())
