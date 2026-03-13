# TaskUp - Task Management API

TaskUp is a FastAPI + SQLModel backend for tasks, projects, teams, and collaboration. It supports Google OAuth2, email/password auth, Kanban columns, task comments with reactions and mentions, subtasks, reminders, activity logs, and a WebSocket channel.

## Project Structure

```
TaskUp/
  alembic/              # Database migrations
  auth/                 # Authentication modules
  constants/            # Enums and action constants
  core/                 # Configuration
  dependencies/         # FastAPI dependencies
  docs/                 # Documentation
  middleware/           # Custom middlewares
  models/               # SQLModel database models
  routers/              # API route handlers
  schemas/              # Pydantic validation schemas
  services/             # Background services + websockets manager
  database.py           # Database configuration
  main.py               # FastAPI application entry point
  api_test.http         # API testing file
  .env                  # Environment variables
```

## Features

- Task CRUD with priorities, due dates, assignees, and completion.
- Projects with automatic default Kanban columns.
- Kanban columns for project boards and task movement.
- Labels and reminders.
- Task comments with emoji reactions and @mentions.
- Subtasks (checklist items) per task.
- Activity logs and HTTP request logs.
- Teams, team members, and project-team linking.
- Auth: Google OAuth2, email/password, JWT access + refresh tokens.
- WebSocket endpoint for realtime events.

## Tech Stack

- Backend: FastAPI (Python 3.9+)
- ORM: SQLModel
- Database: PostgreSQL
- Auth: Google OAuth2 + email/password + JWT
- Migrations: Alembic
- Package manager: UV
- Config: python-decouple

## Quick Start

```bash
uv sync

# create and edit .env (see sample below)
# run migrations
alembic upgrade head

# start server
uvicorn main:app --reload --host 0.0.0.0 --port 8008
```

### Sample .env

```env
DB_NAME=taskpy
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8008/auth/google/callback
GOOGLE_TOKEN_URL=https://oauth2.googleapis.com/token
GOOGLE_USERINFO_URL=https://www.googleapis.com/oauth2/v2/userinfo
```

## API Overview

Core
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check with DB status |

Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/auth/google/login` | Start Google OAuth flow |
| GET | `/auth/google/callback` | OAuth callback handler |
| POST | `/auth/signup` | Email/password signup |
| POST | `/auth/login` | Email/password login |
| POST | `/auth/refresh` | Refresh JWTs |
| POST | `/auth/logout` | Revoke refresh token |
| GET | `/auth/me` | Current user |
| PUT | `/auth/me` | Update current user |

Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | List tasks (filters: `project_id`, `priority`, `assigned_to`, `search`, `column_id`) |
| POST | `/tasks` | Create task |
| GET | `/tasks/{task_id}` | Get task |
| PUT | `/tasks/{task_id}` | Update task |
| DELETE | `/tasks/{task_id}` | Delete task |
| PATCH | `/tasks/{task_id}/complete` | Mark task completed |
| POST | `/tasks/{task_id}/assignees/{user_id}` | Add assignee |
| DELETE | `/tasks/{task_id}/assignees/{user_id}` | Remove assignee |
| GET | `/tasks/{task_id}/assignees` | List assignees |
| POST | `/tasks/{task_id}/labels/{label_id}` | Attach label |
| DELETE | `/tasks/{task_id}/labels/{label_id}` | Detach label |
| GET | `/tasks/{task_id}/labels` | List task labels |

Comments and Mentions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks/{task_id}/comments` | List comments |
| POST | `/tasks/{task_id}/comments` | Add comment |
| PATCH | `/tasks/{task_id}/comments/{comment_id}` | Edit comment |
| DELETE | `/tasks/{task_id}/comments/{comment_id}` | Delete comment |
| POST | `/tasks/{task_id}/comments/{comment_id}/react` | Toggle reaction |
| GET | `/comments/mentions/me` | Unread mentions |
| PATCH | `/comments/mentions/{mention_id}/read` | Mark mention read |
| GET | `/tasks/{task_id}/timeline` | Comment + activity timeline |
| GET | `/tasks/{task_id}/comment-count` | Comment count |

Subtasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks/{task_id}/subtasks` | List subtasks |
| POST | `/tasks/{task_id}/subtasks` | Create subtask |
| PATCH | `/tasks/{task_id}/subtasks/{sub_id}/toggle` | Toggle completion |
| PATCH | `/tasks/{task_id}/subtasks/{sub_id}` | Edit subtask |
| DELETE | `/tasks/{task_id}/subtasks/{sub_id}` | Delete subtask |

Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects` | List projects |
| POST | `/projects` | Create project |
| GET | `/projects/{project_id}` | Get project |
| PUT | `/projects/{project_id}` | Update project |
| DELETE | `/projects/{project_id}` | Delete project |
| GET | `/projects/{project_id}/teams` | Teams linked to project |
| GET | `/projects/{project_id}/members` | Members across linked teams |

Kanban Columns
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/columns/project/{project_id}` | List columns |
| POST | `/columns/project/{project_id}` | Create column |
| PATCH | `/columns/{column_id}` | Update column |
| PATCH | `/columns/{column_id}/reorder` | Reorder column |
| DELETE | `/columns/{column_id}` | Delete column |
| PATCH | `/columns/move-task/{task_id}` | Move task to column |

Labels and Reminders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/labels` | List labels |
| POST | `/labels` | Create label |
| GET | `/labels/{label_id}` | Get label |
| PUT | `/labels/{label_id}` | Update label |
| DELETE | `/labels/{label_id}` | Delete label |
| GET | `/reminders` | List reminders |
| POST | `/reminders` | Create reminder |
| GET | `/reminders/{reminder_id}` | Get reminder |
| PUT | `/reminders/{reminder_id}` | Update reminder |
| DELETE | `/reminders/{reminder_id}` | Delete reminder |
| POST | `/reminders/tasks/{task_id}/reminder` | Create reminder for task |

Activity
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/activity/project/{project_id}` | Project activity logs |
| GET | `/activity/task/{task_id}` | Task activity logs |
| GET | `/activity/user/feed` | User activity feed |
| GET | `/activity/http-logs` | HTTP request logs |
| GET | `/activity/http-logs/user/{user_id}` | User HTTP logs |
| GET | `/activity/stats` | Activity stats |

Teams
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/teams` | List my teams |
| POST | `/teams` | Create team |
| GET | `/teams/{team_id}` | Team detail with members |
| PUT | `/teams/{team_id}` | Update team |
| DELETE | `/teams/{team_id}` | Delete team |
| POST | `/teams/join` | Join team by invite code |
| DELETE | `/teams/{team_id}/leave` | Leave team |
| GET | `/teams/{team_id}/members` | List team members |
| DELETE | `/teams/{team_id}/members/{user_id}` | Remove member |
| PATCH | `/teams/{team_id}/members/{user_id}/promote` | Promote member |
| POST | `/teams/{team_id}/projects/{project_id}` | Link project to team |
| DELETE | `/teams/{team_id}/projects/{project_id}` | Unlink project |
| GET | `/teams/{team_id}/projects` | List team's projects |
| PATCH | `/teams/{team_id}/tasks/{task_id}/assign` | Assign task within team |

Realtime
| Method | Endpoint | Description |
|--------|----------|-------------|
| WS | `/ws?token=JWT` | WebSocket connection |

## Notes

- All protected endpoints expect a Bearer JWT in the `Authorization` header.
- The default port used by `main.py` is `8008`.
