from fastapi import APIRouter, Request, Depends, HTTPException, Query
from sqlmodel import Session, select
import jwt
import requests
from auth.google_auth import oauth
from auth.jwt_handler import create_access_token, create_refresh_token
from database import get_session, engine
from models.user_model import User
from models.refresh_token_model import RefreshToken
from core.config import SECRET_KEY, ALGORITHM, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, GOOGLE_TOKEN_URL, GOOGLE_USERINFO_URL
from auth.security import get_password_hash, verify_password
from schemas.auth_schame import LoginRequest, RefreshTokenRequest, UserSignup
from auth.deps import get_current_user
from pydantic import BaseModel
from typing import Optional

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    }

@router.put("/me")
def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if update_data.name:
        current_user.name = update_data.name
    if update_data.email:
        # Avoid duplicate email check
        existing = session.exec(select(User).where(User.email == update_data.email)).first()
        if existing and existing.id != current_user.id:
            raise HTTPException(400, "Email already in use")
        current_user.email = update_data.email
        
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    }


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
def google_callback(code: str = Query(...)):
    # Step 1: Exchange code for tokens
    token_res = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": GOOGLE_REDIRECT_URI
        }
    ).json()

    if "access_token" not in token_res:
        raise HTTPException(400, "Google token exchange failed")

    google_access = token_res["access_token"]

    # Step 2: Fetch Google user profile
    userinfo = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {google_access}"}
    ).json()

    email = userinfo.get("email")
    google_id = userinfo.get("id")
    name = userinfo.get("name")

    if not email:
        raise HTTPException(400, "Could not fetch Google userinfo")

    # Step 3: Check if user exists or create
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            user = User(email=email, google_id=google_id, name=name)
            session.add(user)
            session.commit()
            session.refresh(user)

        # Step 4: Create our access + refresh tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # Store refresh token
        db_token = RefreshToken(token=refresh_token, user_id=user.id)
        session.add(db_token)
        session.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        }


@router.post("/signup")
def signup(
    signup_data: UserSignup,
    session: Session = Depends(get_session)
):
    """Signup endpoint - creates a new user with hashed password"""
    existing_user = session.exec(select(User).where(User.email == signup_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = get_password_hash(signup_data.password)
    new_user = User(
        email=signup_data.email,
        name=signup_data.name,
        hashed_password=hashed_pwd
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": "User created successfully", "user_id": new_user.id}


@router.post("/login")
def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
):
    """Login endpoint - finds or creates user and returns tokens"""
    user = session.exec(select(User).where(User.email == login_data.email)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.hashed_password:
        raise HTTPException(status_code=400, detail="Please use Google login for this account")

    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Create JWT tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Store refresh token
    db_token = RefreshToken(token=refresh_token, user_id=user.id)
    session.add(db_token)
    session.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }


@router.post("/refresh")
def refresh_token(token_data:RefreshTokenRequest, session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("user_id")

        # Check token exists in DB
        db_token = session.exec(
            select(RefreshToken).where(RefreshToken.token == token_data.refresh_token)
        ).first()

        if not db_token:
            raise HTTPException(
                status_code=401, detail="Refresh token revoked")

        # Issue new tokens
        new_access = create_access_token(user_id)
        new_refresh = create_refresh_token(user_id)

        # Rotate refresh token
        db_token.token = new_refresh
        session.add(db_token)
        session.commit()

        return {
            "access_token": new_access,
            "refresh_token": new_refresh
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/logout")
def logout(refresh_token: RefreshTokenRequest, session: Session = Depends(get_session)):
    db_token = session.exec(
        select(RefreshToken).where(RefreshToken.token == refresh_token.refresh_token)
    ).first()

    if db_token:
        session.delete(db_token)
        session.commit()

    return {"message": "Logged out"}
