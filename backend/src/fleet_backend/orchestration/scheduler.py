"""
Concurrent Fleet Task Scheduler and Worktree Orchestrator.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional
from contracts.events import EventType, FleetEvent
from contracts.tasks import SubTask, Task, TaskStatus
from fleet_backend.core.db import TaskStore
from fleet_backend.core.worktree_manager import WorktreeManager
from fleet_backend.harnesses.base import BaseHarness
from fleet_backend.harnesses.langgraph_harness import LangGraphHarness

logger = logging.getLogger(__name__)


class FleetScheduler:
    """Orchestrates parallel worktree allocations and execution harnesses."""

    def __init__(
        self,
        worktree_manager: WorktreeManager,
        task_store: TaskStore,
        event_callback: Optional[Callable[[FleetEvent], None]] = None,
        llm: Optional[BaseChatModel] = None,
    ):
        self.worktree_mgr = worktree_manager
        self.task_store = task_store
        self.event_callback = event_callback
        self.llm = llm
        self.harnesses: Dict[str, BaseHarness] = {
            "langgraph": LangGraphHarness(llm=self.llm),
        }

    def register_harness(self, harness: BaseHarness) -> None:
        self.harnesses[harness.name] = harness

    async def _emit_event(self, event: FleetEvent) -> None:
        if self.event_callback:
            if asyncio.iscoroutinefunction(self.event_callback):
                await self.event_callback(event)
            else:
                self.event_callback(event)

    async def execute_subtask(self, subtask: SubTask, base_ref: str = "HEAD") -> None:
        """Run a single subtask in an isolated worktree."""
        harness = self.harnesses.get(subtask.assigned_harness, self.harnesses["langgraph"])

        # Allocate worktree
        try:
            env = self.worktree_mgr.create_worktree(task_id=subtask.id, base_ref=base_ref)
            subtask.worktree_path = str(env.worktree_path)
            subtask.branch_name = env.branch_name
            subtask.status = TaskStatus.WORKING

            await self.task_store.update_subtask_status(subtask.id, TaskStatus.WORKING)

            # Stream events from harness
            async for event in harness.execute(subtask, env.worktree_path):
                await self._emit_event(event)

            # Check final diff and status
            diff = self.worktree_mgr.get_diff(subtask.id)
            if diff:
                await self._emit_event(
                    FleetEvent(
                        event_id=f"diff-{subtask.id}",
                        event_type=EventType.DIFF_GENERATED,
                        task_id=subtask.parent_task_id,
                        subtask_id=subtask.id,
                        payload={"git_diff": diff, "branch": env.branch_name},
                    )
                )

        except Exception as e:
            logger.error("Execution error on subtask %s: %s", subtask.id, e)
            await self.task_store.update_subtask_status(subtask.id, TaskStatus.FAILED, error_log=str(e))
            await self._emit_event(
                FleetEvent(
                    event_id=f"err-{subtask.id}",
                    event_type=EventType.SUBTASK_STATUS_CHANGED,
                    task_id=subtask.parent_task_id,
                    subtask_id=subtask.id,
                    payload={"status": TaskStatus.FAILED.value, "error": str(e)},
                )
            )

    async def run_task_fleet(self, task: Task) -> None:
        """Execute all subtasks in parallel (or topological DAG order)."""
        task.status = TaskStatus.WORKING
        await self.task_store.save_task(task)

        # Run independent subtasks concurrently
        coros = [self.execute_subtask(subtask, base_ref=task.base_ref) for subtask in task.subtasks]
        await asyncio.gather(*coros, return_exceptions=True)

        task.status = TaskStatus.READY_TO_MERGE
        await self.task_store.save_task(task)
