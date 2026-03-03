from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from services import log_activity
from database import get_session
from models.reminder_model import Reminder
from models.task_model import Task
from schemas.remindedr_schame import ReminderCreate, ReminderUpdate
from auth.deps import get_current_user
from models.user_model import User

router = APIRouter(prefix="/reminders", tags=["Reminders"])

# CREATE
@router.post("/", response_model=Reminder)
def create_reminder(
    reminder: ReminderCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Verify task belongs to user
    task = session.exec(select(Task).where(Task.id == reminder.task_id, Task.owner_id == current_user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_reminder = Reminder(**reminder.dict())
    session.add(db_reminder)
    session.commit()
    session.refresh(db_reminder)
    return db_reminder


# READ ALL
@router.get("/", response_model=list[Reminder])
def get_reminders(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return session.exec(
        select(Reminder)
        .join(Task, Task.id == Reminder.task_id)
        .where(Task.owner_id == current_user.id)
    ).all()


# READ ONE
@router.get("/{reminder_id}", response_model=Reminder)
def get_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    reminder = session.exec(
        select(Reminder)
        .join(Task, Task.id == Reminder.task_id)
        .where(Reminder.id == reminder_id, Task.owner_id == current_user.id)
    ).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


# UPDATE
@router.put("/{reminder_id}", response_model=Reminder)
def update_reminder(
    reminder_id: int,
    reminder_update: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    reminder = session.exec(
        select(Reminder)
        .join(Task, Task.id == Reminder.task_id)
        .where(Reminder.id == reminder_id, Task.owner_id == current_user.id)
    ).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    for key, value in reminder_update.dict(exclude_unset=True).items():
        setattr(reminder, key, value)

    session.add(reminder)
    session.commit()
    session.refresh(reminder)
    return reminder


# DELETE
@router.delete("/{reminder_id}")
def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    reminder = session.exec(
        select(Reminder)
        .join(Task, Task.id == Reminder.task_id)
        .where(Reminder.id == reminder_id, Task.owner_id == current_user.id)
    ).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    session.delete(reminder)
    session.commit()
    return {"message": "Reminder deleted"}


@router.post("/tasks/{task_id}/reminder")
def create_reminder(task_id: int, data: ReminderCreate, request: Request, session: Session = Depends(get_session)):
    user = request.state.user

    task = session.get(Task, task_id)
    if task.owner_id != user.id:
        raise HTTPException(403, "Only owner can set reminders")

    reminder = Reminder(
        task_id=task_id,
        remind_at=data.remind_at
    )
    session.add(reminder)
    session.commit()
    session.refresh(reminder)
    log_activity(
        session,
        user_id=user.id,
        project_id=task.project_id,
        task_id=task.id,
        action="reminder_triggered",
        details=f"Reminder sent for task '{task.title}'"
    )
    return reminder
