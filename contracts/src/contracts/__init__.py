"""
Contracts Package for Fleet Agent IDE.
Standard typed models and schemas shared between Daemon, CLI, and UI clients.
"""

from contracts.events import (
    DiffUpdateEvent,
    EventType,
    FleetEvent,
    TaskLifecycleEvent,
    TerminalOutputEvent,
)
from contracts.harness import AgentHarness, HarnessExecutionResult
from contracts.tasks import SubTask, SubTaskPlan, Task, TaskDecomposition, TaskStatus

__all__ = [
    "AgentHarness",
    "DiffUpdateEvent",
    "EventType",
    "FleetEvent",
    "HarnessExecutionResult",
    "SubTask",
    "SubTaskPlan",
    "Task",
    "TaskDecomposition",
    "TaskLifecycleEvent",
    "TaskStatus",
    "TerminalOutputEvent",
]
