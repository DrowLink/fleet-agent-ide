"""Agent Harness protocol and contract definitions."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from contracts.events import FleetEvent
from contracts.tasks import SubTask, TaskStatus


@dataclass(frozen=True)
class HarnessExecutionResult:
    """Standard outcome returned by an agent harness."""

    subtask_id: str
    status: TaskStatus
    iterations_used: int
    diff: str
    error_log: str | None = None
    summary: str | None = None


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
