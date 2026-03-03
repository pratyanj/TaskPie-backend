# TaskUp Documentation

Welcome to the TaskUp API documentation! This folder contains comprehensive documentation for the TaskUp task management application.

## 📚 Documentation Index

### [Authentication System](./authentication-system.md)
Complete guide to the JWT-based authentication system including:
- Architecture overview with diagrams
- JWT token handling (access & refresh tokens)
- Middleware authentication
- Dependency injection
- Security best practices
- Troubleshooting guide

### [API Endpoints Reference](./api-endpoints.md)
Detailed API endpoint documentation including:
- All authentication endpoints
- Task management endpoints
- Request/response examples
- Error responses
- cURL examples
- Interactive documentation links

### [Bug Fixes](./bug-fixes.md)
Documentation of all bug fixes and improvements:
- Foreign key constraint violation fix
- Duplicate JWT validation fix
- JWT token payload standardization
- Configuration centralization
- Migration instructions

## 🚀 Quick Start

### 1. Authentication

**Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAi...",
  "refresh_token": "eyJ0eXAi...",
  "token_type": "bearer"
}
```

### 2. Create a Task

```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Task",
    "description": "Task description",
    "priority": 1
  }'
```

### 3. Get All Tasks

```bash
curl -X GET http://localhost:8000/tasks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔧 Important Changes

### Database Migration Required

After applying the bug fixes, you need to run a database migration:

```bash
# Create migration
alembic revision --autogenerate -m "make_project_id_optional_in_task"

# Apply migration
alembic upgrade head
```

### Configuration Updates

Update your production configuration in [`auth/config.py`](file:///P:/pratyanj%20laptop/python/FastAPI/todo/app/TaskUp/auth/config.py):

```python
SECRET_KEY = "your-secure-random-key-here"  # Change this!
```

## 📖 Documentation Files

| File | Description |
|------|-------------|
| [`authentication-system.md`](./authentication-system.md) | Complete authentication system documentation |
| [`api-endpoints.md`](./api-endpoints.md) | API endpoint reference |
| [`bug-fixes.md`](./bug-fixes.md) | Bug fixes and improvements |
| [`README.md`](./README.md) | This file |

## 🔐 Security Notes

> [!WARNING]
> **Production Checklist:**
> - [ ] Change `SECRET_KEY` to a secure random value
> - [ ] Use environment variables for secrets
> - [ ] Enable HTTPS (`https_only=True`)
> - [ ] Set secure CORS origins
> - [ ] Add rate limiting to auth endpoints
> - [ ] Implement token blacklisting
> - [ ] Add logging for auth events

## 🧪 Testing

### Interactive API Documentation

FastAPI provides interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Manual Testing

See the [API Endpoints Reference](./api-endpoints.md#example-usage) for complete testing examples.

## 🐛 Troubleshooting

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| "Token expired" | Use refresh token to get new access token |
| "Refresh token revoked" | Login again |
| "User not found" | Ensure user is registered |
| "Missing Authorization header" | Include `Authorization: Bearer TOKEN` header |

See [Authentication System - Troubleshooting](./authentication-system.md#troubleshooting) for more details.

## 📝 Change Log

### 2025-12-20

**Bug Fixes:**
- Fixed foreign key constraint violation on task creation
- Made `project_id` optional in tasks
- Removed duplicate JWT validation
- Standardized JWT token payload structure
- Centralized authentication configuration

**New Features:**
- JWT middleware for global authentication
- Refresh token rotation
- Logout endpoint
- Improved dependency injection

**Documentation:**
- Created comprehensive authentication documentation
- Created API endpoint reference
- Created bug fixes documentation

## 🤝 Contributing

When making changes to the application:

1. Update relevant documentation files
2. Add entries to the bug fixes or change log
3. Update API endpoint documentation if adding/modifying endpoints
4. Test all authentication flows
5. Create database migrations if needed

## 📞 Support

For issues or questions:
- Check the [Troubleshooting](./authentication-system.md#troubleshooting) section
- Review the [Bug Fixes](./bug-fixes.md) documentation
- Check the [API Reference](./api-endpoints.md) for endpoint details
