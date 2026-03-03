import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlmodel import Session
from database import engine
from models import HTTPRequestLog

PUBLIC_PATHS = [
    "/docs",
    "/openapi.json",
    "/redoc",
    "/favicon.ico"
]

class HTTPRequestLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests to database.
    
    Logs all state-changing requests (POST, PUT, PATCH, DELETE) with:
    - User ID (if authenticated)
    - Request method and path
    - Response status code
    - Request duration
    - IP address and user agent
    
    Skips logging for:
    - Public paths (docs, openapi, etc.)
    - GET requests (to reduce noise)
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip logging for public paths
        if any(request.url.path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)
        
        # Start timer
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log only state-changing requests (POST, PUT, PATCH, DELETE)
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            try:
                with Session(engine) as session:
                    # Get user from request state (set by JWT middleware)
                    user = getattr(request.state, "user", None)
                    user_id = user.id if user else None
                    
                    log_entry = HTTPRequestLog(
                        user_id=user_id,
                        method=request.method,
                        path=request.url.path,
                        status_code=response.status_code,
                        duration_ms=round(duration_ms, 2),
                        ip_address=request.client.host if request.client else None,
                        user_agent=request.headers.get("user-agent")
                    )
                    
                    session.add(log_entry)
                    session.commit()
            except Exception as e:
                # Don't fail request if logging fails
                print(f"HTTP logging error: {e}")
        
        return response
