from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models.project_model import Project
from schemas.project_schema import ProjectCreate, ProjectUpdate, ProjectRead
from auth.deps import get_current_user
from models.user_model import User

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
