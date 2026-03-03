from sqlmodel import Session
from models import ActivityLog
import json
from typing import Optional, Dict, Any

def log_activity(
    session: Session,
    user_id: int,
    action: str,
    details: str,
    project_id: Optional[int] = None,
    task_id: Optional[int] = None,
    extra_data: Optional[Dict[str, Any]] = None
):
    """
    Log a business activity event.
    
    Args:
        session: Database session
        user_id: ID of user performing action
        action: Action constant (use ActivityAction class)
        details: Human-readable description
        project_id: Optional project ID
        task_id: Optional task ID
        extra_data: Optional dict with structured data (old/new values)
    
    Example:
        log_activity(
            session=session,
            user_id=1,
            action=ActivityAction.TASK_UPDATED,
            details="Updated task 'Fix bug' → 'Fix critical bug'",
            task_id=5,
            extra_data={"old_title": "Fix bug", "new_title": "Fix critical bug"}
        )
    """
    entry = ActivityLog(
        user_id=user_id,
        action=action,
        details=details,
        project_id=project_id,
        task_id=task_id,
        extra_data=json.dumps(extra_data) if extra_data else None
    )
    session.add(entry)
    # NOTE: Removed session.commit() - let caller control transaction
