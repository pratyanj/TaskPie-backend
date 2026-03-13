"""
comment_router.py — CRUD for task comments + emoji reactions + @mention notifications
"""
import re
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Dict
from datetime import datetime

from database import get_session
from auth.deps import get_current_user
from models import User, Task, ActivityLog
from models.task_model import TaskComment, CommentReaction, CommentMention
from schemas.comment_schema import CommentCreate, CommentUpdate, CommentRead
from services.activity_service import log_activity
from constants.activity_actions import ActivityAction

router = APIRouter(prefix="/tasks", tags=["Comments"])
mentions_router = APIRouter(prefix="/comments", tags=["Mentions"])

ALLOWED_EMOJIS = {"👍", "✅", "🔥", "❤️", "😂", "😮", "👎"}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_task_or_403(task_id: int, user: User, session: Session) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != user.id and task.assigned_to != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return task


def _build_comment_read(comment: TaskComment, session: Session, current_user_id: int) -> dict:
    author = session.get(User, comment.author_id)

    # Gather reactions grouped by emoji
    reactions_raw = session.exec(
        select(CommentReaction).where(CommentReaction.comment_id == comment.id)
    ).all()

    reaction_map: Dict[str, dict] = {}
    for r in reactions_raw:
        if r.emoji not in reaction_map:
            reaction_map[r.emoji] = {"emoji": r.emoji, "count": 0, "reacted_by_me": False}
        reaction_map[r.emoji]["count"] += 1
        if r.user_id == current_user_id:
            reaction_map[r.emoji]["reacted_by_me"] = True

    return {
        "id": comment.id,
        "task_id": comment.task_id,
        "author_id": comment.author_id,
        "author_name": author.name if author else "Unknown",
        "author_email": author.email if author else "",
        "text": comment.text,
        "created_at": comment.created_at.isoformat(),
        "updated_at": comment.updated_at.isoformat(),
        "is_edited": comment.updated_at > comment.created_at,
        "reactions": list(reaction_map.values()),
    }


def _parse_and_save_mentions(
    text: str, comment: TaskComment, author: User, session: Session
):
    """Extract @name or @email mentions and create CommentMention rows."""
    # Match @ followed by word characters (supports names and partial emails)
    raw_mentions = re.findall(r"@(\w[\w.]*)", text)
    if not raw_mentions:
        return

    for handle in set(raw_mentions):
        # Try matching by name (case-insensitive) or email prefix
        mentioned_user = session.exec(
            select(User).where(
                (User.name.ilike(handle)) | (User.email.ilike(f"{handle}%"))
            )
        ).first()

        if mentioned_user and mentioned_user.id != author.id:
            mention = CommentMention(
                comment_id=comment.id,
                task_id=comment.task_id,
                mentioned_user_id=mentioned_user.id,
                mentioned_by_id=author.id,
            )
            session.add(mention)


# ─── List comments ────────────────────────────────────────────────────────────

@router.get("/{task_id}/comments")
def list_comments(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _get_task_or_403(task_id, current_user, session)
    comments = session.exec(
        select(TaskComment)
        .where(TaskComment.task_id == task_id, TaskComment.is_deleted == False)
        .order_by(TaskComment.created_at)
    ).all()
    return [_build_comment_read(c, session, current_user.id) for c in comments]


# ─── Add comment ─────────────────────────────────────────────────────────────

@router.post("/{task_id}/comments", status_code=201)
def add_comment(
    task_id: int,
    payload: CommentCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    task = _get_task_or_403(task_id, current_user, session)

    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Comment text cannot be empty")

    comment = TaskComment(
        task_id=task_id,
        author_id=current_user.id,
        text=payload.text.strip(),
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)

    # Parse @mentions and create notification records
    _parse_and_save_mentions(comment.text, comment, current_user, session)

    # Log activity
    log_activity(
        session=session,
        user_id=current_user.id,
        task_id=task_id,
        project_id=task.project_id,
        action=ActivityAction.COMMENT_ADDED,
        details=f"{current_user.name} commented on '{task.title}'",
        extra_data={"comment_text": comment.text},
    )
    session.commit()

    return _build_comment_read(comment, session, current_user.id)


# ─── Edit comment ─────────────────────────────────────────────────────────────

@router.patch("/{task_id}/comments/{comment_id}")
def edit_comment(
    task_id: int,
    comment_id: int,
    payload: CommentUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _get_task_or_403(task_id, current_user, session)

    comment = session.get(TaskComment, comment_id)
    if not comment or comment.task_id != task_id or comment.is_deleted:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own comments")

    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Comment text cannot be empty")

    comment.text = payload.text.strip()
    comment.updated_at = datetime.utcnow()
    session.add(comment)

    # Re-parse mentions on edit
    _parse_and_save_mentions(comment.text, comment, current_user, session)
    session.commit()
    session.refresh(comment)

    return _build_comment_read(comment, session, current_user.id)


# ─── Delete comment ───────────────────────────────────────────────────────────

@router.delete("/{task_id}/comments/{comment_id}", status_code=204)
def delete_comment(
    task_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    task = _get_task_or_403(task_id, current_user, session)

    comment = session.get(TaskComment, comment_id)
    if not comment or comment.task_id != task_id or comment.is_deleted:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != current_user.id and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    comment.is_deleted = True
    session.add(comment)

    log_activity(
        session=session,
        user_id=current_user.id,
        task_id=task_id,
        project_id=task.project_id,
        action=ActivityAction.COMMENT_DELETED,
        details=f"{current_user.name} deleted a comment on '{task.title}'",
    )
    session.commit()


# ─── Toggle reaction (add if not exists, remove if already reacted) ───────────

@router.post("/{task_id}/comments/{comment_id}/react")
def toggle_reaction(
    task_id: int,
    comment_id: int,
    body: dict,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Toggle an emoji reaction. body: { "emoji": "👍" }"""
    emoji = body.get("emoji", "").strip()
    if emoji not in ALLOWED_EMOJIS:
        raise HTTPException(status_code=400, detail=f"Emoji must be one of {ALLOWED_EMOJIS}")

    _get_task_or_403(task_id, current_user, session)

    comment = session.get(TaskComment, comment_id)
    if not comment or comment.task_id != task_id or comment.is_deleted:
        raise HTTPException(status_code=404, detail="Comment not found")

    existing = session.exec(
        select(CommentReaction).where(
            CommentReaction.comment_id == comment_id,
            CommentReaction.user_id == current_user.id,
            CommentReaction.emoji == emoji,
        )
    ).first()

    if existing:
        session.delete(existing)
        session.commit()
        return {"action": "removed", "emoji": emoji}
    else:
        reaction = CommentReaction(
            comment_id=comment_id,
            user_id=current_user.id,
            emoji=emoji,
        )
        session.add(reaction)
        session.commit()
        return {"action": "added", "emoji": emoji}


# ─── My mentions (unread) ─────────────────────────────────────────────────────

@mentions_router.get("/mentions/me")
def get_my_mentions(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Returns all unread @mentions of the current user, newest first."""
    mentions = session.exec(
        select(CommentMention)
        .where(
            CommentMention.mentioned_user_id == current_user.id,
            CommentMention.is_read == False,
        )
        .order_by(CommentMention.created_at.desc())
    ).all()

    result = []
    for m in mentions:
        comment = session.get(TaskComment, m.comment_id)
        task = session.get(Task, m.task_id)
        by_user = session.get(User, m.mentioned_by_id)
        result.append({
            "id": m.id,
            "comment_id": m.comment_id,
            "task_id": m.task_id,
            "task_title": task.title if task else None,
            "comment_text": comment.text if comment else None,
            "mentioned_by_name": by_user.name if by_user else "Someone",
            "is_read": m.is_read,
            "created_at": m.created_at.isoformat(),
        })
    return {"mentions": result, "unread_count": len(result)}


@mentions_router.patch("/mentions/{mention_id}/read", status_code=200)
def mark_mention_read(
    mention_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    mention = session.get(CommentMention, mention_id)
    if not mention or mention.mentioned_user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Mention not found")
    mention.is_read = True
    session.add(mention)
    session.commit()
    return {"ok": True}


# ─── Unified Timeline ─────────────────────────────────────────────────────────

@router.get("/{task_id}/timeline")
def get_task_timeline(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _get_task_or_403(task_id, current_user, session)

    comments = session.exec(
        select(TaskComment)
        .where(TaskComment.task_id == task_id, TaskComment.is_deleted == False)
    ).all()

    logs = session.exec(
        select(ActivityLog).where(ActivityLog.task_id == task_id)
    ).all()

    timeline = []

    for c in comments:
        item = _build_comment_read(c, session, current_user.id)
        item["type"] = "comment"
        timeline.append(item)

    for log in logs:
        timeline.append({
            "type": "activity",
            "id": log.id,
            "action": log.action,
            "details": log.details,
            "user_id": log.user_id,
            "created_at": log.created_at.isoformat(),
        })

    timeline.sort(key=lambda x: x["created_at"])
    return {"task_id": task_id, "timeline": timeline, "total": len(timeline)}


# ─── Comment count for a task (used by TaskCard badge) ───────────────────────

@router.get("/{task_id}/comment-count")
def get_comment_count(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _get_task_or_403(task_id, current_user, session)
    count = len(session.exec(
        select(TaskComment)
        .where(TaskComment.task_id == task_id, TaskComment.is_deleted == False)
    ).all())
    return {"task_id": task_id, "count": count}
