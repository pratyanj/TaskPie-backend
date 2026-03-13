"""
kanban_router.py
Endpoints for dynamic Kanban column management and task movement.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from database import get_session
from auth.deps import get_current_user
from models import User, Project, KanbanColumn, Task
from schemas.kanban_schema import (
    KanbanColumnCreate,
    KanbanColumnUpdate,
    KanbanColumnReorder,
    KanbanColumnRead,
)

router = APIRouter(prefix="/columns", tags=["Kanban"])


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_project_or_403(project_id: int, user: User, session: Session) -> Project:
    """Return the project if the user is the owner, else raise 404/403."""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return project


def _get_column_or_403(column_id: int, user: User, session: Session) -> KanbanColumn:
    col = session.get(KanbanColumn, column_id)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")
    _get_project_or_403(col.project_id, user, session)
    return col


def create_default_columns(project_id: int, session: Session) -> None:
    """Create the four default Kanban columns for a new project."""
    defaults = [
        {"name": "To Do",       "color": "#6366F1", "order": 0, "is_done_column": False},
        {"name": "In Progress", "color": "#F59E0B", "order": 1, "is_done_column": False},
        {"name": "In Review",   "color": "#8B5CF6", "order": 2, "is_done_column": False},
        {"name": "Done",        "color": "#10B981", "order": 3, "is_done_column": True},
    ]
    for d in defaults:
        col = KanbanColumn(project_id=project_id, **d)
        session.add(col)
    session.commit()


# ─── List columns for a project ───────────────────────────────────────────────

@router.get("/project/{project_id}", response_model=List[KanbanColumnRead])
def get_project_columns(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Return all Kanban columns for a project, ordered."""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    cols = session.exec(
        select(KanbanColumn)
        .where(KanbanColumn.project_id == project_id,
               KanbanColumn.is_deleted == False)
        .order_by(KanbanColumn.order)
    ).all()

    # Auto-create defaults if project has no columns yet
    if not cols:
        create_default_columns(project_id, session)
        cols = session.exec(
            select(KanbanColumn)
            .where(KanbanColumn.project_id == project_id,
                   KanbanColumn.is_deleted == False)
            .order_by(KanbanColumn.order)
        ).all()

    return cols


# ─── Create a new column ──────────────────────────────────────────────────────

@router.post("/project/{project_id}", response_model=KanbanColumnRead, status_code=201)
def create_column(
    project_id: int,
    payload: KanbanColumnCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _get_project_or_403(project_id, current_user, session)

    # Determine order: append to end if not specified
    if payload.order is None:
        last = session.exec(
            select(KanbanColumn)
            .where(KanbanColumn.project_id == project_id,
                   KanbanColumn.is_deleted == False)
            .order_by(KanbanColumn.order.desc())
        ).first()
        order = (last.order + 1) if last else 0
    else:
        order = payload.order

    col = KanbanColumn(
        project_id=project_id,
        name=payload.name,
        color=payload.color or "#6366F1",
        order=order,
        is_done_column=payload.is_done_column or False,
    )
    session.add(col)
    session.commit()
    session.refresh(col)
    return col


# ─── Update a column (rename / color) ─────────────────────────────────────────

@router.patch("/{column_id}", response_model=KanbanColumnRead)
def update_column(
    column_id: int,
    payload: KanbanColumnUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    col = _get_column_or_403(column_id, current_user, session)

    if payload.name is not None:
        col.name = payload.name
    if payload.color is not None:
        col.color = payload.color
    if payload.is_done_column is not None:
        col.is_done_column = payload.is_done_column

    session.add(col)
    session.commit()
    session.refresh(col)
    return col


# ─── Reorder columns ──────────────────────────────────────────────────────────

@router.patch("/{column_id}/reorder", response_model=KanbanColumnRead)
def reorder_column(
    column_id: int,
    payload: KanbanColumnReorder,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    col = _get_column_or_403(column_id, current_user, session)

    # Shift sibling columns to keep orders unique
    siblings = session.exec(
        select(KanbanColumn)
        .where(KanbanColumn.project_id == col.project_id,
               KanbanColumn.id != col.id,
               KanbanColumn.is_deleted == False)
        .order_by(KanbanColumn.order)
    ).all()

    old_order = col.order
    new_order = payload.new_order

    for sib in siblings:
        if old_order < new_order:
            if old_order < sib.order <= new_order:
                sib.order -= 1
                session.add(sib)
        else:
            if new_order <= sib.order < old_order:
                sib.order += 1
                session.add(sib)

    col.order = new_order
    session.add(col)
    session.commit()
    session.refresh(col)
    return col


# ─── Delete a column ────────────────────────────────────────────────────────

@router.delete("/{column_id}", status_code=204)
def delete_column(
    column_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    col = _get_column_or_403(column_id, current_user, session)

    # Unlink tasks but keep them alive (column_id → None)
    tasks = session.exec(select(Task).where(Task.column_id == column_id)).all()
    for t in tasks:
        t.column_id = None
        session.add(t)

    col.is_deleted = True
    session.add(col)
    session.commit()


# ─── Move a task to a different column ────────────────────────────────────────

@router.patch("/move-task/{task_id}", response_model=dict)
def move_task(
    task_id: int,
    column_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Move a task to a new column. If the column is_done_column, also sets completed=True."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    col = session.get(KanbanColumn, column_id)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")

    task.column_id = column_id
    if col.is_done_column:
        task.completed = True
    else:
        task.completed = False

    session.add(task)
    session.commit()
    return {"task_id": task_id, "column_id": column_id, "completed": task.completed}
