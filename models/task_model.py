from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from models.base_model import SoftDeleteMixin, TimestampMixin

class Task(SoftDeleteMixin, TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str]
    completed: bool = False
    priority: int = Field(default=2)  # 1=High, 2=Medium, 3=Low
    due_date: Optional[datetime]

    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    assigned_to: Optional[int] = Field(default=None, foreign_key="user.id")
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    column_id: Optional[int] = Field(default=None, foreign_key="kanban_column.id")


class TaskLabel(SoftDeleteMixin, TimestampMixin, table=True):
    task_id: int = Field(foreign_key="task.id", primary_key=True)
    label_id: int = Field(foreign_key="label.id", primary_key=True)

class TaskAssignee(SoftDeleteMixin, TimestampMixin, table=True):
    task_id: int = Field(foreign_key="task.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)


class TaskComment(SoftDeleteMixin, TimestampMixin, table=True):
    __tablename__ = "task_comment"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id", index=True)
    author_id: int = Field(foreign_key="user.id")
    text: str


class CommentReaction(SQLModel, table=True):
    """One emoji reaction per user per comment (unique: comment_id + user_id + emoji)."""
    __tablename__ = "comment_reaction"

    id: Optional[int] = Field(default=None, primary_key=True)
    comment_id: int = Field(foreign_key="task_comment.id", index=True)
    user_id: int = Field(foreign_key="user.id")
    emoji: str  # e.g. "👍", "✅", "🔥", "❤️", "😂"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CommentMention(SQLModel, table=True):
    """Tracks @user mentions inside comments — used for in-app notifications."""
    __tablename__ = "comment_mention"

    id: Optional[int] = Field(default=None, primary_key=True)
    comment_id: int = Field(foreign_key="task_comment.id", index=True)
    task_id: int = Field(foreign_key="task.id")
    mentioned_user_id: int = Field(foreign_key="user.id", index=True)
    mentioned_by_id: int = Field(foreign_key="user.id")
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Subtask(SQLModel, table=True):
    """A lightweight checklist item belonging to a parent Task."""
    __tablename__ = "subtask"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id", index=True)
    title: str
    completed: bool = Field(default=False)
    order: int = Field(default=0)       # display order within the task
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
