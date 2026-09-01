"""Base Harness abstractions for Fleet Backend."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncGenerator
from contracts.tasks import SubTask
from contracts.events import FleetEvent


class BaseHarness(ABC):
    """Abstract base class for all agent harnesses."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier of the harness driver."""
        pass

    @abstractmethod
    async def execute(
        self,
        subtask: SubTask,
        worktree_path: Path,
    ) -> AsyncGenerator[FleetEvent, None]:
        """Execute a subtask within the assigned isolated worktree."""
        pass
