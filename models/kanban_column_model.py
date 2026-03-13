from sqlmodel import SQLModel, Field
from typing import Optional
from models.base_model import TimestampMixin, SoftDeleteMixin


class KanbanColumn(TimestampMixin, SoftDeleteMixin, table=True):
    __tablename__ = "kanban_column"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=False)
    color: str = Field(default="#6366F1")        # hex accent for column header
    order: int = Field(default=0)                # display order within project
    project_id: int = Field(foreign_key="project.id", index=True)
    is_done_column: bool = Field(default=False)  # tasks here get completed=True
