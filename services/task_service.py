from models import Task
from services import log_activity
from constants.activity_actions import ActivityAction
from sqlmodel import Session
from services.websocket_manager import ConnectionManager

async def update_task(task_id: int, data, user, session: Session):
    """
    Update a task and log the activity.
    
    Args:
        task_id: ID of task to update
        data: Update data with title, priority, etc.
        user: User performing the update
        session: Database session
    
    Returns:
        Updated task object
    """
    task = session.get(Task, task_id)
    
    # Capture old values for logging
    old_title = task.title
    old_priority = task.priority
    
    # Update fields
    task.title = data.title or task.title
    task.priority = data.priority or task.priority
    
    session.add(task)
    session.commit()
    
    # Log activity with extra_data
    log_activity(
        session=session,
        user_id=user.id,
        project_id=task.project_id,
        task_id=task.id,
        action=ActivityAction.TASK_UPDATED,
        details=f"Updated task '{old_title}' → '{task.title}'",
        extra_data={
            "old_title": old_title,
            "new_title": task.title,
            "old_priority": old_priority,
            "new_priority": task.priority
        }
    )
    session.commit()  # Commit the activity log
    await ConnectionManager.broadcast({
        "event": "task_updated",
        "task_id": task.id,
        "title": task.title,
        "priority": task.priority,
    })
    return task
