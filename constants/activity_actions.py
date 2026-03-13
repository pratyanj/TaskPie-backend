"""Activity action constants for type-safe logging"""

class ActivityAction:
    """Constants for activity log actions"""
    
    # Task actions
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_DELETED = "task_deleted"
    
    # Assignee actions
    ASSIGNEE_ADDED = "assignee_added"
    ASSIGNEE_REMOVED = "assignee_removed"
    
    # Project actions
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    PROJECT_ARCHIVED = "project_archived"
    
    # Label actions
    LABEL_CREATED = "label_created"
    LABEL_ATTACHED = "label_attached"
    LABEL_DETACHED = "label_detached"
    LABEL_DELETED = "label_deleted"

    # Comment actions
    COMMENT_ADDED = "comment_added"
    COMMENT_DELETED = "comment_deleted"

    # Column / board actions
    TASK_MOVED = "task_moved"
