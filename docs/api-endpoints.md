# API Endpoints Reference

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints except public routes require JWT authentication via `Authorization` header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## Public Endpoints

### Google OAuth Login

Initiates Google OAuth flow.

```http
GET /auth/google/login
```

**Response:** Redirects to Google login page

---

### Google OAuth Callback

Handles Google OAuth callback and returns tokens.

```http
GET /auth/google/callback
```

**Query Parameters:**
- `code` - OAuth authorization code (provided by Google)
- `state` - OAuth state parameter (provided by Google)

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

### Login

Login with email address.

```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `404 Not Found` - User not found

---

### Refresh Token

Exchange refresh token for new access and refresh tokens.

```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid token type
- `401 Unauthorized` - Refresh token revoked
- `401 Unauthorized` - Token expired
- `401 Unauthorized` - Invalid token

---

### Logout

Revoke refresh token.

```http
POST /auth/logout
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "message": "Logged out"
}
```

---

## Protected Endpoints

> [!IMPORTANT]
> All endpoints below require authentication via `Authorization: Bearer YOUR_ACCESS_TOKEN` header.

---

## Tasks

### Permissions Summary

The following table shows what actions each role can perform on tasks:

| Action | Task Owner | Project Owner | Task Assignee |
|--------|------------|---------------|---------------|
| **Create task** | ✅ Yes | ✅ Yes | ❌ No |
| **View task** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Update task** | ✅ Yes | ✅ Yes | ❌ No |
| **Delete task** | ✅ Yes | ✅ Yes | ❌ No |
| **Complete task** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Add assignee** | ✅ Yes | ✅ Yes | ❌ No |
| **Remove assignee** | ✅ Yes | ✅ Yes | ❌ No |
| **View assignees** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Attach label** | ✅ Yes | ❌ No | ❌ No |
| **Detach label** | ✅ Yes | ❌ No | ❌ No |
| **View labels** | ✅ Yes | ❌ No | ❌ No |

> [!NOTE]
> **Task Owner**: User who created the task
> **Project Owner**: Owner of the project the task belongs to
> **Task Assignee**: User assigned as a collaborator to the task

---

### Create Task

Create a new task.

```http
POST /tasks/
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Implement user authentication",
  "description": "Add OAuth2 authentication with Google",
  "priority": 1,
  "due_date": "2024-12-31T23:59:59",
  "project_id": 1  // Optional
}
```

**Field Descriptions:**
- `title` (required) - Task title
- `description` (optional) - Task description
- `priority` (optional) - Priority level (1=High, 2=Medium, 3=Low), default: 2
- `due_date` (optional) - Due date in ISO 8601 format
- `project_id` (optional) - ID of project this task belongs to

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Implement user authentication",
  "description": "Add OAuth2 authentication with Google",
  "completed": false,
  "priority": 1,
  "due_date": "2024-12-31T23:59:59",
  "owner_id": 1,
  "project_id": 1,
  "created_at": "2025-12-20T07:40:53.329408"
}
```

**Error Responses:**
- `401 Unauthorized` - Missing or invalid token
- `500 Internal Server Error` - Invalid project_id (if project doesn't exist)

---

### Get All Tasks

Get all tasks for the authenticated user.

```http
GET /tasks/
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "Implement user authentication",
    "description": "Add OAuth2 authentication with Google",
    "completed": false,
    "priority": 1,
    "due_date": "2024-12-31T23:59:59",
    "owner_id": 1,
    "project_id": 1,
    "created_at": "2025-12-20T07:40:53.329408"
  },
  {
    "id": 2,
    "title": "Write documentation",
    "description": null,
    "completed": true,
    "priority": 2,
    "due_date": null,
    "owner_id": 1,
    "project_id": null,
    "created_at": "2025-12-20T08:15:22.123456"
  }
]
```

---

### Get Single Task

Get a specific task by ID.

```http
GET /tasks/{task_id}
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Path Parameters:**
- `task_id` - ID of the task

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Implement user authentication",
  "description": "Add OAuth2 authentication with Google",
  "completed": false,
  "priority": 1,
  "due_date": "2024-12-31T23:59:59",
  "owner_id": 1,
  "project_id": 1,
  "created_at": "2025-12-20T07:40:53.329408"
}
```

**Error Responses:**
- `404 Not Found` - Task not found or doesn't belong to user

---

### Update Task

Update an existing task.

> [!IMPORTANT]
> **Permissions:** Only the task owner or project owner can update a task.

```http
PUT /tasks/{task_id}
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Path Parameters:**
- `task_id` - ID of the task

**Request Body:** (all fields optional)
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true,
  "priority": 2,
  "due_date": "2025-01-15T23:59:59"
}
```

**Permission Matrix:**

| Scenario | Task Owner | Project Owner | Can Update? |
|----------|------------|---------------|-------------|
| User owns the task | ✅ Yes | ❌ No | ✅ **Yes** |
| User owns the project | ❌ No | ✅ Yes | ✅ **Yes** |
| User owns both | ✅ Yes | ✅ Yes | ✅ **Yes** |
| User owns neither | ❌ No | ❌ No | ❌ **No (403)** |
| Task has no project | ✅ Yes | N/A | ✅ **Yes** (if task owner) |

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Updated title",
  "description": "Updated description",
  "completed": true,
  "priority": 2,
  "due_date": "2025-01-15T23:59:59",
  "owner_id": 1,
  "project_id": 1,
  "created_at": "2025-12-20T07:40:53.329408"
}
```

**Error Responses:**
- `404 Not Found` - Task not found
- `403 Forbidden` - User is neither task owner nor project owner

---

### Delete Task

Delete a task.

> [!IMPORTANT]
> **Permissions:** Only the task owner or project owner can delete a task.

```http
DELETE /tasks/{task_id}
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Path Parameters:**
- `task_id` - ID of the task

**Response:** `200 OK`
```json
{
  "message": "Task deleted successfully"
}
```

**Error Responses:**
- `404 Not Found` - Task not found
- `403 Forbidden` - User is neither task owner nor project owner

---

### Mark Task as Completed

Mark a task as completed.

> [!IMPORTANT]
> **Permissions:** Task owner, project owner, or task assignee can mark a task as completed.

```http
PATCH /tasks/{task_id}/complete
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Path Parameters:**
- `task_id` - ID of the task

**Permission Matrix:**

| Scenario | Task Owner | Project Owner | Task Assignee | Can Complete? |
|----------|------------|---------------|---------------|---------------|
| User owns the task | ✅ Yes | ❌ No | ❌ No | ✅ **Yes** |
| User owns the project | ❌ No | ✅ Yes | ❌ No | ✅ **Yes** |
| User is assigned to task | ❌ No | ❌ No | ✅ Yes | ✅ **Yes** |
| User owns both task & project | ✅ Yes | ✅ Yes | ❌ No | ✅ **Yes** |
| User is assignee & owner | ✅ Yes | ❌ No | ✅ Yes | ✅ **Yes** |
| User has no relation | ❌ No | ❌ No | ❌ No | ❌ **No (403)** |

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Implement user authentication",
  "description": "Add OAuth2 authentication with Google",
  "completed": true,
  "priority": 1,
  "due_date": "2024-12-31T23:59:59",
  "owner_id": 1,
  "project_id": 1,
  "created_at": "2025-12-20T07:40:53.329408"
}
```

**Error Responses:**
- `404 Not Found` - Task not found
- `403 Forbidden` - User is not task owner, project owner, or assignee

---

### Add Assignee to Task

Add a collaborator/assignee to a task.

> [!IMPORTANT]
> **Permissions:** Only the task owner or project owner can add assignees.

```http
POST /tasks/{task_id}/assignees/{user_id}
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Path Parameters:**
- `task_id` - ID of the task
- `user_id` - ID of the user to assign

**Response:** `200 OK`
```json
{
  "message": "User user@example.com assigned to task successfully"
}
```

**Error Responses:**
- `404 Not Found` - Task not found or user not found
- `403 Forbidden` - User is neither task owner nor project owner
- `400 Bad Request` - User is already assigned to this task

---

### Remove Assignee from Task

Remove a collaborator/assignee from a task.

> [!IMPORTANT]
> **Permissions:** Only the task owner or project owner can remove assignees.

```http
DELETE /tasks/{task_id}/assignees/{user_id}
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Path Parameters:**
- `task_id` - ID of the task
- `user_id` - ID of the user to remove

**Response:** `200 OK`
```json
{
  "message": "User removed from task successfully"
}
```

**Error Responses:**
- `404 Not Found` - Task not found or user is not assigned to this task
- `403 Forbidden` - User is neither task owner nor project owner

---

### Get Task Assignees

Get all assignees/collaborators for a task.

```http
GET /tasks/{task_id}/assignees
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Path Parameters:**
- `task_id` - ID of the task

**Response:** `200 OK`
```json
[
  {
    "id": 2,
    "email": "collaborator1@example.com",
    "name": "John Doe",
    "google_id": "123456789"
  },
  {
    "id": 3,
    "email": "collaborator2@example.com",
    "name": "Jane Smith",
    "google_id": "987654321"
  }
]
```

**Error Responses:**
- `404 Not Found` - Task not found

---

### Attach Label to Task

Attach a label to a task.

```http
POST /tasks/{task_id}/labels/{label_id}
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Path Parameters:**
- `task_id` - ID of the task
- `label_id` - ID of the label

**Response:** `200 OK`
```json
{
  "message": "Label attached to task"
}
```

**Error Responses:**
- `404 Not Found` - Task or label not found
- `400 Bad Request` - Label already attached

---

### Detach Label from Task

Remove a label from a task.

```http
DELETE /tasks/{task_id}/labels/{label_id}
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Path Parameters:**
- `task_id` - ID of the task
- `label_id` - ID of the label

**Response:** `200 OK`
```json
{
  "message": "Label detached from task"
}
```

**Error Responses:**
- `404 Not Found` - Task not found or label not attached

---

### Get Task Labels

Get all labels attached to a task.

```http
GET /tasks/{task_id}/labels
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Path Parameters:**
- `task_id` - ID of the task

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "urgent",
    "color": "#FF0000",
    "owner_id": 1
  },
  {
    "id": 2,
    "name": "backend",
    "color": "#00FF00",
    "owner_id": 1
  }
]
```

**Error Responses:**
- `404 Not Found` - Task not found

---

## Common Error Responses

### 401 Unauthorized

Missing or invalid authentication token.

```json
{
  "detail": "Missing or invalid Authorization header"
}
```

```json
{
  "detail": "Token expired"
}
```

```json
{
  "detail": "Invalid token"
}
```

### 403 Forbidden

User does not have permission to perform the action.

```json
{
  "detail": "You cannot edit this task. Only the task owner or project owner can update it."
}
```

```json
{
  "detail": "You cannot delete this task. Only the task owner or project owner can delete it."
}
```

### 404 Not Found

Resource not found.

```json
{
  "detail": "Task not found"
}
```

```json
{
  "detail": "User not found"
}
```

### 500 Internal Server Error

Server error (e.g., database constraint violation).

```json
{
  "detail": "Internal server error"
}
```

---

## Example Usage

### Complete Authentication Flow

```bash
# 1. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Response:
# {
#   "access_token": "eyJ0eXAi...",
#   "refresh_token": "eyJ0eXAi...",
#   "token_type": "bearer"
# }

# 2. Create a task
curl -X POST http://localhost:8000/tasks/ \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Task",
    "description": "Task description",
    "priority": 1
  }'

# 3. Get all tasks
curl -X GET http://localhost:8000/tasks/ \
  -H "Authorization: Bearer eyJ0eXAi..."

# 4. When access token expires, refresh it
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJ0eXAi..."}'

# 5. Logout
curl -X POST http://localhost:8000/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJ0eXAi..."}'
```

---

## Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These interfaces allow you to:
- View all endpoints
- Test endpoints directly in the browser
- See request/response schemas
- Authenticate and test protected routes
