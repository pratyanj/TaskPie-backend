"""
subtask_router.py — Checklist items for tasks (Phase C)
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from auth.deps import get_current_user
from constants.activity_actions import ActivityAction
from database import get_session
from models import Task, User
from models.task_model import Subtask
from schemas.subtask_schema import SubtaskCreate, SubtaskRead, SubtaskUpdate
from services.activity_service import log_activity

router = APIRouter(prefix="/tasks", tags=["Subtasks"])


def _get_task_or_403(task_id: int, user: User, session: Session) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != user.id and task.assigned_to != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return task


def _to_read(sub: Subtask) -> dict:
    return {
        "id": sub.id,
        "task_id": sub.task_id,
        "title": sub.title,
        "completed": sub.completed,
        "order": sub.order,
        "created_at": sub.created_at.isoformat(),
        "updated_at": sub.updated_at.isoformat(),
    }


@router.get("/{task_id}/subtasks")
def list_subtasks(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _get_task_or_403(task_id, current_user, session)
    subs = session.exec(
        select(Subtask).where(Subtask.task_id == task_id).order_by(Subtask.order)
    ).all()
    total = len(subs)
    done = sum(1 for subtask in subs if subtask.completed)
    return {
        "subtasks": [_to_read(subtask) for subtask in subs],
        "total": total,
        "completed": done,
        "progress": round(done / total * 100) if total else 0,
    }


@router.post("/{task_id}/subtasks", response_model=SubtaskRead, status_code=201)
def add_subtask(
    task_id: int,
    payload: SubtaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    task = _get_task_or_403(task_id, current_user, session)

    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="Subtask title cannot be empty")

    existing = session.exec(select(Subtask).where(Subtask.task_id == task_id)).all()
    order = payload.order if payload.order else len(existing)

    subtask = Subtask(
        task_id=task_id,
        title=payload.title.strip(),
        order=order,
    )
    session.add(subtask)
    session.commit()
    session.refresh(subtask)

    log_activity(
        session=session,
        user_id=current_user.id,
        task_id=task_id,
        project_id=task.project_id,
        action=ActivityAction.TASK_UPDATED,
        details=f"Subtask added: '{subtask.title}'",
    )
    session.commit()

    return _to_read(subtask)


@router.patch("/{task_id}/subtasks/{sub_id}/toggle", response_model=SubtaskRead)
def toggle_subtask(
    task_id: int,
    sub_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _get_task_or_403(task_id, current_user, session)

    subtask = session.get(Subtask, sub_id)
    if not subtask or subtask.task_id != task_id:
        raise HTTPException(status_code=404, detail="Subtask not found")

    subtask.completed = not subtask.completed
    subtask.updated_at = datetime.utcnow()
    session.add(subtask)
    session.commit()
    session.refresh(subtask)
    return _to_read(subtask)


@router.patch("/{task_id}/subtasks/{sub_id}", response_model=SubtaskRead)
def edit_subtask(
    task_id: int,
    sub_id: int,
    payload: SubtaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _get_task_or_403(task_id, current_user, session)

    subtask = session.get(Subtask, sub_id)
    if not subtask or subtask.task_id != task_id:
        raise HTTPException(status_code=404, detail="Subtask not found")

    if payload.title is not None:
        if not payload.title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        subtask.title = payload.title.strip()
        subtask.updated_at = datetime.utcnow()

    session.add(subtask)
    session.commit()
    session.refresh(subtask)
    return _to_read(subtask)


@router.delete("/{task_id}/subtasks/{sub_id}", status_code=204)
def delete_subtask(
    task_id: int,
    sub_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _get_task_or_403(task_id, current_user, session)

    subtask = session.get(Subtask, sub_id)
    if not subtask or subtask.task_id != task_id:
        raise HTTPException(status_code=404, detail="Subtask not found")

    session.delete(subtask)
    session.commit()
