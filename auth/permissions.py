from fastapi import HTTPException, status
from sqlmodel import Session
from models import Task, TaskAssignee
from models import Project


def assert_project_owner(user_id: int, project: Project):
    """
    Verify that the user is the owner of the project.

    Args:
        user_id (int): The ID of the user.
        project (Project): The project instance to check.

    Raises:
        HTTPException: 403 Forbidden if the user is not the owner.
    """
    if project.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can perform this action."
        )


def assert_task_owner(user_id: int, task: Task):
    """
    Verify that the user is the owner of the task.

    Args:
        user_id (int): The ID of the user.
        task (Task): The task instance to check.

    Raises:
        HTTPException: 403 Forbidden if the user is not the owner.
    """
    if task.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the task owner can perform this action."
        )


def assert_task_collaborator(user_id: int, task_id: int, session: Session):
    """
    Verify that the user is assigned to the specified task.

    Args:
        user_id (int): The ID of the user.
        task_id (int): The ID of the task.
        session (Session): The database session.

    Raises:
        HTTPException: 403 Forbidden if the user is not assigned to the task.
    """
    rel = session.get(TaskAssignee, (task_id, user_id))
    if not rel:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this task."
        )
