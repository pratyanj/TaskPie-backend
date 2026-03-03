erDiagram
    USER ||--o{ PROJECT : owns
    USER ||--o{ TASK : creates
    PROJECT ||--o{ TASK : contains

    TASK }o--o{ LABEL : tagged_with
    TASK }o--o{ USER : assigned_to

    TASK ||--o{ REMINDER : has

    USER {
        int id
        string email
        string google_id
        string name
    }

    PROJECT {
        int id
        string name
        string description
    }

    TASK {
        int id
        string title
        bool completed
        int priority
        datetime due_date
    }

    LABEL {
        int id
        string name
        string color
    }

    REMINDER {
        int id
        datetime remind_at
        bool sent
    }
