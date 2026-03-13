from fastapi import FastAPI
from fastapi.openapi.models import SecurityScheme as SecuritySchemeModel
from routers.task_router import router as task_router
from routers.project_router import router as project_router
from routers.label_router import router as label_router
from routers.reminder_router import router as reminder_router
from routers.auth_router import router as auth_router
from routers.activity_router import router as activity_router
from routers.team_router import router as team_router
from routers.kanban_router import router as kanban_router
from routers.comment_router import router as comment_router, mentions_router
from routers.subtask_router import router as subtask_router

from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from middleware import JWTAuthMiddleware, HTTPRequestLogMiddleware
from services import start_scheduler
from fastapi.openapi.utils import get_openapi

from database import engine
from sqlmodel import SQLModel, text
import models  # noqa: F401 — ensures all models are registered with SQLModel metadata

# Create all tables that don't exist yet
SQLModel.metadata.create_all(engine)

app = FastAPI(
    title="TaskUp API",
    swagger_ui_init_oauth={},
)

# --- Inject Bearer token auth into Swagger UI ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Add BearerAuth security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT access token (without the 'Bearer ' prefix)",
        }
    }
    # Apply it globally to all endpoints
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key="pratyanj_secret_key",
    same_site="lax",
    https_only=False  # set True in production with HTTPS
)
# Add middlewares in correct order (HTTP logging runs after JWT auth)
app.add_middleware(HTTPRequestLogMiddleware)  # Logs HTTP requests
app.add_middleware(JWTAuthMiddleware)         # Authenticates users
app.include_router(task_router)
app.include_router(project_router)
app.include_router(label_router)
app.include_router(reminder_router)
app.include_router(auth_router)
app.include_router(activity_router)
app.include_router(team_router)
app.include_router(kanban_router)
app.include_router(comment_router)
app.include_router(mentions_router)
app.include_router(subtask_router)

start_scheduler() 

@app.get("/")
def read_root():
    return {"message": "Welcome to TaskUp API"}

@app.get("/health")
def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return {"status": "unhealthy", "database": "disconnected"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8008)
    