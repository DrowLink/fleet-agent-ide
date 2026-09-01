"""Base Harness abstractions for Fleet Backend."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from pathlib import Path

from contracts.events import FleetEvent
from contracts.tasks import SubTask


class BaseHarness(ABC):
    """Abstract base class for all agent harnesses."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier of the harness driver."""

    @abstractmethod
    async def execute(
        self,
        subtask: SubTask,
        worktree_path: Path,
    ) -> AsyncGenerator[FleetEvent, None]:
        """Execute a subtask within the assigned isolated worktree."""
