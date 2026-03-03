from fastapi import Depends, HTTPException
from jose import jwt
from sqlmodel import Session, select

from database import get_session
from models import User

SECRET_KEY = "CHANGE_ME"
ALGORITHM = "HS256"

def get_current_user(
    token: str = Depends(...),  # JWT later
    session: Session = Depends(get_session),
) -> User:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("sub")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    return user
