from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Task, TaskAssignee
from models import User

def get_task_or_404(task_id: int, session: Session):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def is_owner_or_assignee(task_id: int, user: User, session: Session):
    task = get_task_or_404(task_id, session)

    if task.owner_id == user.id:
        return task

    assigned = session.exec(
        select(TaskAssignee).where(
            TaskAssignee.task_id == task_id,
            TaskAssignee.user_id == user.id,
        )
    ).first()

    if not assigned:
        raise HTTPException(status_code=403, detail="Access denied")

    return task


def is_owner(task_id: int, user: User, session: Session):
    task = get_task_or_404(task_id, session)

    if task.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only owner allowed")

    return task
