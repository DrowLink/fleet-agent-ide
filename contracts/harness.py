"""Agent Harness protocol and contract definitions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Optional, Protocol, runtime_checkable
from contracts.tasks import SubTask, TaskStatus
from contracts.events import FleetEvent


@dataclass(frozen=True)
class HarnessExecutionResult:
    """Standard outcome returned by an agent harness."""
    subtask_id: str
    status: TaskStatus
    iterations_used: int
    diff: str
    error_log: Optional[str] = None
    summary: Optional[str] = None


@runtime_checkable
class AgentHarness(Protocol):
    """Pluggable Agent Harness interface."""

    name: str

    async def execute(
        self,
        subtask: SubTask,
        worktree_path: Path,
    ) -> AsyncGenerator[FleetEvent, None]:
        """Execute a subtask within an isolated worktree and yield progress events."""
        ...
