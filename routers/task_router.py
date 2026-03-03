from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from schemas.task_schema import TaskCreate, TaskUpdate, TaskRead
from models.task_model import Task, TaskLabel, TaskAssignee
from models.project_model import Project
from models.label_model import Label
from auth.deps import get_current_user
from models.user_model import User
from services.activity_service import log_activity
from constants.activity_actions import ActivityAction

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# CREATE
@router.post("/", response_model=TaskRead)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    db_task = Task(
        **task.dict(),
        owner_id=current_user.id
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    
    # Log activity
    log_activity(
        session=session,
        user_id=current_user.id,
        task_id=db_task.id,
        project_id=db_task.project_id,
        action=ActivityAction.TASK_CREATED,
        details=f"{current_user.name} created task '{db_task.title}'"
    )
    session.commit()
    
    return db_task


# READ ALL
@router.get("/", response_model=list[Task])
def get_tasks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return session.exec(select(Task).where(Task.owner_id == current_user.id)).all()


# READ ONE
@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = session.exec(select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# UPDATE
@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Get the task
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Permission check: only task owner or project owner can update
    is_task_owner = task.owner_id == current_user.id
    is_project_owner = False
    
    if task.project_id:
        project = session.get(Project, task.project_id)
        if project:
            is_project_owner = project.owner_id == current_user.id
    
    if not is_task_owner and not is_project_owner:
        raise HTTPException(
            status_code=403,
            detail="You cannot edit this task. Only the task owner or project owner can update it."
        )

    # Update task fields
    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# DELETE
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get the task
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Permission check: only task owner or project owner can delete
    is_task_owner = task.owner_id == current_user.id
    is_project_owner = False
    
    if task.project_id:
        project = session.get(Project, task.project_id)
        if project:
            is_project_owner = project.owner_id == current_user.id
    
    if not is_task_owner and not is_project_owner:
        raise HTTPException(
            status_code=403,
            detail="You cannot delete this task. Only the task owner or project owner can delete it."
        )
    
    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/labels/{label_id}")
def attach_label_to_task(
    task_id: int,
    label_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    task = session.exec(select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    label = session.exec(select(Label).where(Label.id == label_id, Label.owner_id == current_user.id)).first()
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")

    exists = session.exec(
        select(TaskLabel).where(
            TaskLabel.task_id == task_id,
            TaskLabel.label_id == label_id
        )
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="Label already attached")

    session.add(TaskLabel(task_id=task_id, label_id=label_id))
    session.commit()

    return {"message": "Label attached to task"}

@router.delete("/{task_id}/labels/{label_id}")
def detach_label_from_task(
    task_id: int,
    label_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    task = session.exec(select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_label = session.exec(
        select(TaskLabel).where(
            TaskLabel.task_id == task_id,
            TaskLabel.label_id == label_id
        )
    ).first()

    if not task_label:
        raise HTTPException(status_code=404, detail="Label not attached")

    session.delete(task_label)
    session.commit()

    return {"message": "Label detached from task"}

@router.get("/{task_id}/labels", response_model=list[Label])
def get_task_labels(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    task = session.exec(select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return session.exec(
        select(Label)
        .join(TaskLabel, TaskLabel.label_id == Label.id)
        .where(TaskLabel.task_id == task_id)
    ).all()


# MARK TASK AS COMPLETED
@router.patch("/{task_id}/complete", response_model=Task)
def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Mark a task as completed.
    
    Allowed for:
    - Task owner
    - Project owner
    - Task assignee
    """
    # Get the task
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Permission check: task owner, project owner, or task assignee
    is_task_owner = task.owner_id == current_user.id
    is_project_owner = False
    is_assignee = False
    
    # Check if user is project owner
    if task.project_id:
        project = session.get(Project, task.project_id)
        if project:
            is_project_owner = project.owner_id == current_user.id
    
    # Check if user is assigned to the task
    assignee_relation = session.get(TaskAssignee, (task_id, current_user.id))
    if assignee_relation:
        is_assignee = True
    
    if not (is_task_owner or is_project_owner or is_assignee):
        raise HTTPException(
            status_code=403,
            detail="You cannot modify this task. Only the task owner, project owner, or task assignees can mark it as completed."
        )
    
    # Mark task as completed
    task.completed = True
    session.add(task)
    session.commit()
    
    # Log activity
    log_activity(
        session=session,
        user_id=current_user.id,
        task_id=task_id,
        project_id=task.project_id,
        action=ActivityAction.TASK_COMPLETED,
        details=f"{current_user.name} completed task '{task.title}'"
    )
    session.commit()
    
    session.refresh(task)
    return task


# ADD ASSIGNEE/COLLABORATOR TO TASK
@router.post("/{task_id}/assignees/{user_id}")
def add_assignee(
    task_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Add a collaborator/assignee to a task.
    
    Allowed for:
    - Task owner
    - Project owner
    """
    # Get the task
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Permission check: only task owner or project owner
    is_task_owner = task.owner_id == current_user.id
    is_project_owner = False
    
    if task.project_id:
        project = session.get(Project, task.project_id)
        if project:
            is_project_owner = project.owner_id == current_user.id
    
    if not (is_task_owner or is_project_owner):
        raise HTTPException(
            status_code=403,
            detail="Only the task owner or project owner can assign collaborators."
        )
    
    # Check if user to be assigned exists
    user_to_assign = session.get(User, user_id)
    if not user_to_assign:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already assigned
    existing_assignment = session.get(TaskAssignee, (task_id, user_id))
    if existing_assignment:
        raise HTTPException(status_code=400, detail="User is already assigned to this task")
    
    # Add assignment
    assignment = TaskAssignee(task_id=task_id, user_id=user_id)
    session.add(assignment)
    session.commit()
    
    # Log activity
    log_activity(
        session=session,
        user_id=current_user.id,
        task_id=task_id,
        project_id=task.project_id,
        action=ActivityAction.ASSIGNEE_ADDED,
        details=f"{current_user.name} assigned {user_to_assign.name} to task '{task.title}'",
        extra_data={
            "assignee_id": user_id,
            "assignee_email": user_to_assign.email,
            "assignee_name": user_to_assign.name
        }
    )
    session.commit()
    
    return {"message": f"User {user_to_assign.email} assigned to task successfully"}


# REMOVE ASSIGNEE/COLLABORATOR FROM TASK
@router.delete("/{task_id}/assignees/{user_id}")
def remove_assignee(
    task_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Remove a collaborator/assignee from a task.
    
    Allowed for:
    - Task owner
    - Project owner
    """
    # Get the task
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Permission check: only task owner or project owner
    is_task_owner = task.owner_id == current_user.id
    is_project_owner = False
    
    if task.project_id:
        project = session.get(Project, task.project_id)
        if project:
            is_project_owner = project.owner_id == current_user.id
    
    if not (is_task_owner or is_project_owner):
        raise HTTPException(
            status_code=403,
            detail="Only the task owner or project owner can remove collaborators."
        )
    
    # Check if assignment exists
    assignment = session.get(TaskAssignee, (task_id, user_id))
    if not assignment:
        raise HTTPException(status_code=404, detail="User is not assigned to this task")
    
    # Get user info for logging
    removed_user = session.get(User, user_id)
    
    # Remove assignment
    session.delete(assignment)
    session.commit()
    
    # Log activity
    log_activity(
        session=session,
        user_id=current_user.id,
        task_id=task_id,
        project_id=task.project_id,
        action=ActivityAction.ASSIGNEE_REMOVED,
        details=f"{current_user.name} removed {removed_user.name if removed_user else 'user'} from task '{task.title}'",
        extra_data={
            "removed_user_id": user_id,
            "removed_user_email": removed_user.email if removed_user else None
        }
    )
    session.commit()
    
    return {"message": "User removed from task successfully"}


# GET TASK ASSIGNEES
@router.get("/{task_id}/assignees", response_model=list[User])
def get_task_assignees(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get all assignees/collaborators for a task.
    """
    # Get the task
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get all assignees
    assignees = session.exec(
        select(User)
        .join(TaskAssignee, TaskAssignee.user_id == User.id)
        .where(TaskAssignee.task_id == task_id)
    ).all()
    
    return assignees
