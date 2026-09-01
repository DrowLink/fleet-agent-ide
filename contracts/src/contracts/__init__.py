"""
Contracts Package for Fleet Agent IDE.
Standard typed models and schemas shared between Daemon, CLI, and UI clients.
"""

from contracts.tasks import Task, SubTask, TaskStatus, SubTaskPlan, TaskDecomposition
from contracts.events import (
    FleetEvent,
    EventType,
    TaskLifecycleEvent,
    TerminalOutputEvent,
    DiffUpdateEvent,
)
from contracts.harness import AgentHarness, HarnessExecutionResult

__all__ = [
    "Task",
    "SubTask",
    "TaskStatus",
    "SubTaskPlan",
    "TaskDecomposition",
    "FleetEvent",
    "EventType",
    "TaskLifecycleEvent",
    "TerminalOutputEvent",
    "DiffUpdateEvent",
    "AgentHarness",
    "HarnessExecutionResult",
]
