from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CommentCreate(BaseModel):
    text: str


class CommentUpdate(BaseModel):
    text: str


class CommentRead(BaseModel):
    id: int
    task_id: int
    author_id: int
    author_name: str          # resolved from User — injected by the router
    author_email: str
    text: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
