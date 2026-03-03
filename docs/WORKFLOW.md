# TaskUp - Technical Workflow Documentation

## 🔄 System Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Client]
        B[Mobile App]
        C[API Testing Tools]
    end
    
    subgraph "API Gateway"
        D[FastAPI Application]
        E[Authentication Middleware]
        F[CORS Middleware]
    end
    
    subgraph "Business Logic"
        G[Task Router]
        H[Project Router]
        I[Label Router]
        J[Reminder Router]
        K[Auth Router]
    end
    
    subgraph "Data Layer"
        L[SQLModel ORM]
        M[Alembic Migrations]
        N[PostgreSQL Database]
    end
    
    subgraph "External Services"
        O[Google OAuth2]
        P[Email Service]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
    F --> J
    F --> K
    
    G --> L
    H --> L
    I --> L
    J --> L
    K --> O
    
    L --> N
    M --> N
    
    J --> P
```

## 🔐 Authentication Flow Detail

```mermaid
sequenceDiagram
    participant U as User
    participant C as Client App
    participant API as FastAPI Server
    participant G as Google OAuth
    participant DB as Database
    participant JWT as JWT Service

    Note over U,JWT: Initial Login Process
    U->>C: Click "Login with Google"
    C->>API: GET /auth/google/login
    API->>G: Redirect to Google OAuth
    G->>U: Show Google Login Page
    U->>G: Enter credentials
    G->>API: Callback with auth code
    API->>G: Exchange code for tokens
    G->>API: Return user info + tokens
    API->>DB: Check if user exists
    
    alt User doesn't exist
        API->>DB: Create new user record
    else User exists
        API->>DB: Update last login
    end
    
    API->>JWT: Generate JWT token
    JWT->>API: Return signed token
    API->>C: Return JWT + user data
    C->>U: Login successful
    
    Note over U,JWT: Subsequent API Calls
    U->>C: Make API request
    C->>API: Request with JWT in header
    API->>JWT: Validate token
    JWT->>API: Token valid/invalid
    
    alt Token valid
        API->>DB: Process request
        DB->>API: Return data
        API->>C: Return response
    else Token invalid
        API->>C: 401 Unauthorized
    end
```

## 📋 Task Management Workflow

```mermaid
stateDiagram-v2
    [*] --> Planning
    
    Planning --> Created : Create Task
    Created --> InProgress : Start Work
    Created --> Cancelled : Cancel Task
    
    InProgress --> Paused : Pause Work
    InProgress --> Completed : Complete Task
    InProgress --> Blocked : External Dependency
    
    Paused --> InProgress : Resume Work
    Paused --> Cancelled : Cancel Task
    
    Blocked --> InProgress : Dependency Resolved
    Blocked --> Cancelled : Cannot Resolve
    
    Completed --> [*]
    Cancelled --> [*]
    
    note right of Created
        Task created with:
        - Title & Description
        - Priority Level
        - Due Date
        - Project Assignment
    end note
    
    note right of InProgress
        Task being worked on:
        - Progress tracking
        - Time logging
        - Status updates
    end note
```

## 🏗️ Database Operations Flow

```mermaid
flowchart TD
    A[API Request] --> B{Authentication Check}
    B -->|Failed| C[Return 401]
    B -->|Success| D[Parse Request Body]
    
    D --> E{Validate Schema}
    E -->|Invalid| F[Return 422]
    E -->|Valid| G[Check Permissions]
    
    G -->|Denied| H[Return 403]
    G -->|Allowed| I{Operation Type}
    
    I -->|CREATE| J[Insert Record]
    I -->|READ| K[Query Records]
    I -->|UPDATE| L[Find & Update]
    I -->|DELETE| M[Find & Delete]
    
    J --> N{DB Success?}
    K --> O{Records Found?}
    L --> P{Update Success?}
    M --> Q{Delete Success?}
    
    N -->|Yes| R[Return 201 Created]
    N -->|No| S[Return 500 Error]
    
    O -->|Yes| T[Return 200 OK]
    O -->|No| U[Return 404 Not Found]
    
    P -->|Yes| V[Return 200 Updated]
    P -->|No| W[Return 404/500]
    
    Q -->|Yes| X[Return 204 Deleted]
    Q -->|No| Y[Return 404/500]
```

## 🔄 Project Development Lifecycle

```mermaid
gitgraph
    commit id: "Initial Setup"
    commit id: "Database Models"
    commit id: "API Schemas"
    
    branch feature/authentication
    checkout feature/authentication
    commit id: "Google OAuth Setup"
    commit id: "JWT Implementation"
    commit id: "Auth Middleware"
    
    checkout main
    merge feature/authentication
    commit id: "Auth Integration"
    
    branch feature/task-management
    checkout feature/task-management
    commit id: "Task CRUD"
    commit id: "Task-Label Relations"
    commit id: "Task Permissions"
    
    checkout main
    merge feature/task-management
    commit id: "Task System Complete"
    
    branch feature/reminders
    checkout feature/reminders
    commit id: "Reminder Model"
    commit id: "Scheduler Service"
    commit id: "Email Integration"
    
    checkout main
    merge feature/reminders
    commit id: "v1.0 Release"
```

## 📊 Data Flow Architecture

```mermaid
flowchart LR
    subgraph "Input Layer"
        A1[HTTP Request]
        A2[Request Headers]
        A3[Request Body]
    end
    
    subgraph "Validation Layer"
        B1[Pydantic Schema]
        B2[Type Validation]
        B3[Business Rules]
    end
    
    subgraph "Business Layer"
        C1[Router Handler]
        C2[Service Logic]
        C3[Permission Check]
    end
    
    subgraph "Data Access Layer"
        D1[SQLModel ORM]
        D2[Query Builder]
        D3[Transaction Manager]
    end
    
    subgraph "Storage Layer"
        E1[PostgreSQL]
        E2[Connection Pool]
        E3[Indexes]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B3
    
    B1 --> C1
    B2 --> C2
    B3 --> C3
    
    C1 --> D1
    C2 --> D2
    C3 --> D3
    
    D1 --> E1
    D2 --> E2
    D3 --> E3
```

## 🧪 Testing Strategy

```mermaid
pyramid
    title Testing Pyramid
    
    section Unit Tests
        Models
        Schemas
        Utilities
    
    section Integration Tests
        API Endpoints
        Database Operations
        Authentication Flow
    
    section E2E Tests
        Complete User Workflows
        Cross-Service Integration
```

## 🚀 Deployment Pipeline

```mermaid
flowchart TD
    A[Developer Push] --> B[GitHub Actions]
    B --> C{Tests Pass?}
    C -->|No| D[Notify Developer]
    C -->|Yes| E[Build Docker Image]
    
    E --> F[Push to Registry]
    F --> G{Environment}
    
    G -->|Staging| H[Deploy to Staging]
    G -->|Production| I[Deploy to Production]
    
    H --> J[Run Integration Tests]
    J --> K{Tests Pass?}
    K -->|No| L[Rollback]
    K -->|Yes| M[Staging Ready]
    
    I --> N[Blue-Green Deployment]
    N --> O[Health Check]
    O --> P{Healthy?}
    P -->|No| Q[Rollback]
    P -->|Yes| R[Switch Traffic]
```

## 🔧 Error Handling Flow

```mermaid
flowchart TD
    A[Exception Occurs] --> B{Exception Type}
    
    B -->|ValidationError| C[Return 422]
    B -->|HTTPException| D[Return Status Code]
    B -->|DatabaseError| E[Log Error]
    B -->|AuthError| F[Return 401/403]
    B -->|Unknown| G[Log & Return 500]
    
    C --> H[Format Error Response]
    D --> H
    E --> I[Return 500]
    F --> H
    G --> I
    
    H --> J[Send to Client]
    I --> J
    
    E --> K[Alert Monitoring]
    G --> K
```

## 📈 Performance Monitoring

```mermaid
graph TB
    subgraph "Metrics Collection"
        A[Request Latency]
        B[Database Query Time]
        C[Memory Usage]
        D[CPU Usage]
        E[Error Rates]
    end
    
    subgraph "Monitoring Tools"
        F[Prometheus]
        G[Grafana]
        H[AlertManager]
    end
    
    subgraph "Alerting"
        I[Slack Notifications]
        J[Email Alerts]
        K[PagerDuty]
    end
    
    A --> F
    B --> F
    C --> F
    D --> F
    E --> F
    
    F --> G
    F --> H
    
    H --> I
    H --> J
    H --> K
```

## 🔄 API Versioning Strategy

```mermaid
timeline
    title API Evolution
    
    section v1.0
        Basic CRUD : Tasks
                   : Projects
                   : Labels
    
    section v1.1
        Authentication : Google OAuth
                      : JWT Tokens
    
    section v1.2
        Advanced Features : Reminders
                         : Task Dependencies
                         : File Attachments
    
    section v2.0
        Breaking Changes : New Schema
                        : Improved Performance
                        : GraphQL Support
```

This documentation provides a comprehensive technical overview for your team members and seniors to understand the project architecture, workflows, and development processes.