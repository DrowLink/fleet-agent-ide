"""Task, SubTask and DAG schema contracts."""

from __future__ import annotations

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Lifecycle status of a task or subtask."""
    PLANNING = "planning"
    WORKING = "working"
    NEEDS_REVIEW = "needs_review"
    READY_TO_MERGE = "ready_to_merge"
    MERGED = "merged"
    FAILED = "failed"
    COMPLETED = "completed"


class SubTaskPlan(BaseModel):
    """Decomposition plan element."""
    title: str = Field(description="Short descriptive title of the atomic subtask")
    description: str = Field(description="Detailed instructions of what to modify or create")
    target_files: List[str] = Field(default_factory=list, description="Target relative filepaths touched")
    test_command: Optional[str] = Field(default=None, description="Command to validate this subtask")
    dependencies: List[str] = Field(default_factory=list, description="IDs of prerequisite subtasks")


class TaskDecomposition(BaseModel):
    """Overall decomposition from the supervisor planner."""
    subtasks: List[SubTaskPlan] = Field(description="Ordered list of atomic subtasks")


class SubTask(BaseModel):
    """Concrete atomic subtask assigned to an isolated worktree worker."""
    id: str
    parent_task_id: str
    title: str
    description: str
    target_files: List[str] = Field(default_factory=list)
    test_command: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PLANNING
    assigned_harness: str = "langgraph"
    assigned_worker_id: Optional[str] = None
    worktree_path: Optional[str] = None
    branch_name: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    error_log: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))


class Task(BaseModel):
    """High-level issue or feature request."""
    id: str
    title: str
    prompt: str
    base_ref: str = "main"
    status: TaskStatus = TaskStatus.PLANNING
    subtasks: List[SubTask] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
