from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select
from datetime import datetime
from database import engine
from models import Reminder, Task, User

scheduler = BackgroundScheduler()

def check_reminders():
    with Session(engine) as session:
        now = datetime.utcnow()

        reminders = session.exec(
            select(Reminder).where(
                Reminder.remind_at <= now,
                Reminder.sent == False
            )
        ).all()

        for r in reminders:
            task = session.get(Task, r.task_id)
            user = session.get(User, task.owner_id)

            # TODO: Replace with real email/push notification
            print(f"🔔 Reminder for {user.email}: {task.title}")

            r.sent = True
            session.add(r)

        session.commit()


def start_scheduler():
    scheduler.add_job(check_reminders, "interval", seconds=30)
    scheduler.start()
