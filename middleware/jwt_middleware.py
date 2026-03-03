import jwt
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlmodel import Session, select
from database import get_session, engine
from models import User
from core.config import SECRET_KEY,ALGORITHM


EXACT_PUBLIC_PATHS = {
    "/auth/signup",
    "/auth/login",
    "/auth/refresh",
    "/auth/google/login",
    "/auth/google/callback",
    "/health",
    "/",
}

PREFIX_PUBLIC_PATHS = {
    "/docs",
    "/openapi.json",
}


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip auth for public paths
        if path in EXACT_PUBLIC_PATHS or any(path.startswith(p) for p in PREFIX_PUBLIC_PATHS):
            return await call_next(request)

        # Read Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Missing or invalid Authorization header"},
                status_code=401
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")

            if user_id is None:
                return JSONResponse({"detail": "Invalid token payload"}, status_code=401)

            # Get user from DB
            with Session(engine) as session:
                user = session.get(User, user_id)
                if not user:
                    return JSONResponse({"detail": "User not found"}, status_code=401)

                # Attach user to request
                request.state.user = user

        except jwt.ExpiredSignatureError:
            return JSONResponse(
                {"detail": "ACCESS_TOKEN_EXPIRED"},
                status_code=401
            )

        except jwt.InvalidTokenError:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)

        # Continue to actual route
        return await call_next(request)
