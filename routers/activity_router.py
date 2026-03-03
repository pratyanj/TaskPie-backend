from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from models import ActivityLog, HTTPRequestLog
from database import get_session
from auth.deps import get_current_user
from models import User
from typing import Optional

router = APIRouter(prefix="/activity", tags=["Activity"])


@router.get("/project/{project_id}")
def get_project_activity(
    project_id: int,
    limit: int = Query(50, le=100, description="Maximum number of logs to return"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get business activity logs for a project.
    
    Returns user-friendly activity logs showing what happened in the project.
    """
    logs = session.exec(
        select(ActivityLog)
        .where(ActivityLog.project_id == project_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    
    total = session.exec(
        select(ActivityLog)
        .where(ActivityLog.project_id == project_id)
    ).all()
    
    return {
        "logs": logs,
        "total": len(total),
        "limit": limit,
        "offset": offset
    }


@router.get("/task/{task_id}")
def get_task_activity(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get business activity logs for a specific task.
    
    Shows the complete history of what happened to the task.
    """
    logs = session.exec(
        select(ActivityLog)
        .where(ActivityLog.task_id == task_id)
        .order_by(ActivityLog.created_at.desc())
    ).all()
    
    return {"logs": logs, "total": len(logs)}


@router.get("/user/feed")
def get_user_activity_feed(
    limit: int = Query(20, le=100, description="Maximum number of logs to return"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get activity feed for the current user.
    
    Shows all activities performed by the user across all projects and tasks.
    """
    query = select(ActivityLog).where(ActivityLog.user_id == current_user.id)
    
    if action:
        query = query.where(ActivityLog.action == action)
    
    logs = session.exec(
        query.order_by(ActivityLog.created_at.desc()).limit(limit)
    ).all()
    
    return {
        "logs": logs,
        "total": len(logs),
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name
        }
    }


@router.get("/http-logs")
def get_http_request_logs(
    limit: int = Query(50, le=100, description="Maximum number of logs to return"),
    method: Optional[str] = Query(None, description="Filter by HTTP method (GET, POST, etc.)"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get HTTP request logs for security audit and debugging.
    
    Shows technical details of HTTP requests made to the API.
    Useful for security monitoring and debugging.
    """
    query = select(HTTPRequestLog).order_by(HTTPRequestLog.created_at.desc())
    
    if method:
        query = query.where(HTTPRequestLog.method == method)
    
    if status_code:
        query = query.where(HTTPRequestLog.status_code == status_code)
    
    logs = session.exec(query.limit(limit)).all()
    
    return {
        "logs": logs,
        "total": len(logs),
        "filters": {
            "method": method,
            "status_code": status_code
        }
    }


@router.get("/http-logs/user/{user_id}")
def get_user_http_logs(
    user_id: int,
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get HTTP request logs for a specific user.
    
    Useful for tracking a specific user's API activity.
    """
    logs = session.exec(
        select(HTTPRequestLog)
        .where(HTTPRequestLog.user_id == user_id)
        .order_by(HTTPRequestLog.created_at.desc())
        .limit(limit)
    ).all()
    
    return {"logs": logs, "total": len(logs), "user_id": user_id}


@router.get("/stats")
def get_activity_stats(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get activity statistics for the current user.
    
    Returns counts of different activity types.
    """
    from constants.activity_actions import ActivityAction
    
    total_activities = len(session.exec(
        select(ActivityLog).where(ActivityLog.user_id == current_user.id)
    ).all())
    
    tasks_created = len(session.exec(
        select(ActivityLog)
        .where(ActivityLog.user_id == current_user.id)
        .where(ActivityLog.action == ActivityAction.TASK_CREATED)
    ).all())
    
    tasks_completed = len(session.exec(
        select(ActivityLog)
        .where(ActivityLog.user_id == current_user.id)
        .where(ActivityLog.action == ActivityAction.TASK_COMPLETED)
    ).all())
    
    return {
        "user_id": current_user.id,
        "total_activities": total_activities,
        "tasks_created": tasks_created,
        "tasks_completed": tasks_completed
    }
