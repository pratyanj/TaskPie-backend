from fastapi import Depends, HTTPException, status, Request
from models import User

# async def get_current_user(request: Request) -> User:
async def get_current_user(request: Request) -> User:
    """
    Retrieve the current user from request.state.
    The user is already authenticated and attached by JWTAuthMiddleware.
    """
    user = getattr(request.state, "user", None)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user