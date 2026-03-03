from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class HTTPRequestLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Request info
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    method: str  # GET, POST, PUT, DELETE, etc.
    path: str    # /tasks/1
    status_code: int  # 200, 404, 500, etc.
    
    # Performance
    duration_ms: float  # Request duration in milliseconds
    
    # Security
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
