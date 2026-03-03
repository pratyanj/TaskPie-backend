# TaskUp - Task Management API

A comprehensive task management system built with FastAPI, SQLModel, and PostgreSQL. This project provides a RESTful API for managing tasks, projects, labels, and reminders with Google OAuth2 authentication.

## 🏗️ Project Architecture

```
TaskUp/
├── 📁 alembic/              # Database migrations
├── 📁 auth/                 # Authentication modules
├── 📁 dependencies/         # FastAPI dependencies
├── 📁 doc/                  # Documentation
├── 📁 models/               # SQLModel database models
├── 📁 routers/              # API route handlers
├── 📁 schemas/              # Pydantic validation schemas
├── 📁 services/             # Background services
├── 📄 database.py           # Database configuration
├── 📄 main.py               # FastAPI application entry point
├── 📄 api_test.http         # API testing file
└── 📄 .env                  # Environment variables
```

## 🚀 Features

- **Task Management**: Create, read, update, delete tasks with priorities and due dates
- **Project Organization**: Group tasks into projects
- **Label System**: Categorize tasks with colored labels
- **Reminders**: Set time-based reminders for tasks
- **Google OAuth2**: Secure authentication with Google
- **Custom Auth**: Internal email/password login and signup support
- **Password Security**: Bcrypt-based one-way password hashing
- **Health Monitoring**: Built-in health check endpoints
- **Database Migrations**: Alembic for schema management

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: Google OAuth2 + Custom Email/Password
- **Password Hashing**: Bcrypt with Passlib
- **Migrations**: Alembic
- **Package Management**: UV
- **Environment**: Python-decouple

## 📊 Database Schema

```mermaid
erDiagram
    User ||--o{ Project : owns
    User ||--o{ Task : owns
    User ||--o{ Label : owns
    Project ||--o{ Task : contains
    Task ||--o{ Reminder : has
    Task }o--o{ Label : tagged_with

    User {
        int id PK
        string email
        string name
        string google_id
        string hashed_password
        datetime created_at
    }

    Project {
        int id PK
        string name
        string description
        int owner_id FK
        datetime created_at
    }

    Task {
        int id PK
        string title
        string description
        boolean completed
        int priority
        datetime due_date
        int owner_id FK
        int project_id FK
        datetime created_at
    }

    Label {
        int id PK
        string name
        string color
        int owner_id FK
    }

    Reminder {
        int id PK
        int task_id FK
        datetime remind_at
        boolean sent
        datetime created_at
    }

    TaskLabel {
        int task_id FK
        int label_id FK
    }
```

## 🔄 API Workflow

### 1. Authentication Flows

#### Google OAuth2 Flow
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Google
    participant Database

    Client->>API: GET /auth/google/login
    API->>Google: Redirect to Google OAuth
    Google->>Client: Authorization Code
    Client->>API: GET /auth/google/callback?code=...
    API->>Google: Exchange code for tokens
    Google->>API: User info + tokens
    API->>Database: Create/Update user
    API->>Client: JWT token + user data
```

#### Custom Email/Password Flow
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Database

    Note over Client,API: Signup
    Client->>API: POST /auth/signup (email, name, password)
    API->>API: Hash Password (Bcrypt)
    API->>Database: Save User
    API->>Client: Success Response

    Note over Client,API: Login
    Client->>API: POST /auth/login (email, password)
    API->>Database: Fetch User by Email
    API->>API: Verify Password Hash
    API->>Client: JWT Access + Refresh Tokens
```

### 2. Task Management Flow
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Database

    Note over Client,Database: Create Project First
    Client->>API: POST /projects
    API->>Database: Insert project
    Database->>API: Project created
    API->>Client: Project data

    Note over Client,Database: Create Task
    Client->>API: POST /tasks
    API->>Database: Insert task with project_id
    Database->>API: Task created
    API->>Client: Task data

    Note over Client,Database: Add Labels
    Client->>API: POST /tasks/{id}/labels/{label_id}
    API->>Database: Create task-label relationship
    API->>Client: Success response
```

### 3. Complete CRUD Operations
```mermaid
flowchart TD
    A[Client Request] --> B{Authentication}
    B -->|Valid| C[Route Handler]
    B -->|Invalid| D[401 Unauthorized]
    
    C --> E{Operation Type}
    E -->|CREATE| F[Validate Schema]
    E -->|READ| G[Query Database]
    E -->|UPDATE| H[Find & Update]
    E -->|DELETE| I[Find & Delete]
    
    F --> J[Insert to DB]
    G --> K[Return Data]
    H --> L[Update DB]
    I --> M[Remove from DB]
    
    J --> N[Return Created]
    K --> O[Return Found]
    L --> P[Return Updated]
    M --> Q[Return Success]
```

## 🚦 API Endpoints

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check with DB status |
| GET | `/` | Welcome message |

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/auth/google/login` | Initiate Google OAuth redirect |
| GET | `/auth/google/callback` | Google OAuth callback handler |
| POST | `/auth/signup` | Register a new user with email/password |
| POST | `/auth/login` | Login with email/password |
| POST | `/auth/refresh` | Refresh expired access tokens |
| POST | `/auth/logout` | Invalidate session / refresh token |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create new task |
| GET | `/tasks/{id}` | Get task by ID |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |
| POST | `/tasks/{id}/labels/{label_id}` | Attach label to task |
| DELETE | `/tasks/{id}/labels/{label_id}` | Detach label from task |
| GET | `/tasks/{id}/labels` | Get task labels |

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects` | List all projects |
| POST | `/projects` | Create new project |
| GET | `/projects/{id}` | Get project by ID |
| PUT | `/projects/{id}` | Update project |
| DELETE | `/projects/{id}` | Delete project |

### Labels & Reminders
Similar CRUD patterns for `/labels` and `/reminders` endpoints.

## 🔧 Setup Instructions

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd TaskUp

# Install dependencies with UV
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your database and Google OAuth credentials
```

### 2. Database Setup
```bash
# Run migrations
alembic upgrade head

# Or create new migration
alembic revision --autogenerate -m "description"
```

### 3. Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth2 credentials
5. Add your credentials to `.env`

### 4. Run the Application
```bash
# Development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🧪 Testing

Use the provided `api_test.http` file with your HTTP client:

```http
# Test health endpoint
GET http://localhost:8000/health

# Create a project
POST http://localhost:8000/projects
Content-Type: application/json

{
  "name": "My Project",
  "description": "Project description"
}
```

## 📝 Development Workflow

### 1. Adding New Features
```mermaid
flowchart LR
    A[Create Model] --> B[Create Schema]
    B --> C[Create Router]
    C --> D[Add to main.py]
    D --> E[Create Migration]
    E --> F[Test API]
    F --> G[Update Documentation]
```

### 2. Database Changes
```bash
# 1. Modify models in models/
# 2. Generate migration
alembic revision --autogenerate -m "add new field"
# 3. Review migration file
# 4. Apply migration
alembic upgrade head
```

### 3. Git Workflow
```bash
# Feature development
git checkout -b feature/new-feature
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# Create pull request for review
```

## 🔒 Security Considerations

- Environment variables for sensitive data
- Google OAuth2 & Bcrypt password hashing
- JWT (JSON Web Tokens) with rotation for session security
- Input validation with Pydantic schemas
- SQL injection prevention with SQLModel
- CORS configuration for production

## 📈 Performance Optimization

- Database indexing on frequently queried fields
- Connection pooling with SQLAlchemy
- Async/await for database operations
- Response caching for static data

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```env
DATABASE_URL=postgresql://user:pass@host:port/db
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

## 👥 Team Collaboration

### Code Review Checklist
- [ ] Models follow naming conventions
- [ ] Schemas validate all inputs
- [ ] Error handling implemented
- [ ] Tests added for new features
- [ ] Documentation updated
- [ ] Migration files reviewed

### Development Standards
- Use conventional commit messages
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write docstrings for complex functions
- Test all API endpoints

## 📞 Support

For questions or issues:
1. Check existing documentation
2. Review API test file for examples
3. Check database migrations
4. Contact team lead for architecture decisions

---

**Built with ❤️ using FastAPI and modern Python tools**