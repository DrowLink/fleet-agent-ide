"""Event contracts for real-time SSE / WebSocket streaming."""

from __future__ import annotations

import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from contracts.tasks import TaskStatus


class EventType(str, Enum):
    """Supported real-time event types."""
    TASK_STATUS_CHANGED = "task.status_changed"
    SUBTASK_STATUS_CHANGED = "subtask.status_changed"
    WORKTREE_CREATED = "worktree.created"
    WORKTREE_REMOVED = "worktree.removed"
    TERMINAL_OUTPUT = "terminal.output"
    TEST_VALIDATION_RESULT = "test.validation_result"
    DIFF_GENERATED = "diff.generated"
    HARNESS_LOG = "harness.log"


class FleetEvent(BaseModel):
    """Base envelope for all fleet streaming events."""
    event_id: str
    event_type: EventType
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    task_id: str
    subtask_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class TaskLifecycleEvent(BaseModel):
    """Payload when a task or subtask status changes."""
    task_id: str
    subtask_id: Optional[str] = None
    old_status: Optional[TaskStatus] = None
    new_status: TaskStatus
    summary: Optional[str] = None


class TerminalOutputEvent(BaseModel):
    """Payload for live PTY command / test execution output."""
    subtask_id: str
    stream: str = "stdout"  # stdout, stderr, pty
    chunk: str
    is_completed: bool = False
    exit_code: Optional[int] = None


class DiffUpdateEvent(BaseModel):
    """Payload when a worker produces git diff changes."""
    subtask_id: str
    worktree_path: str
    git_diff: str
    files_changed: list[str] = Field(default_factory=list)
