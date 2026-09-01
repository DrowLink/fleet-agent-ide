"""Unit tests for Fleet contracts."""

from contracts.events import EventType, FleetEvent
from contracts.tasks import SubTask, Task, TaskStatus


def test_task_creation_and_defaults():
    task = Task(
        id="task-test-01",
        title="Test Feature",
        prompt="Implement a feature",
    )
    assert task.id == "task-test-01"
    assert task.status == TaskStatus.PLANNING
    assert task.base_ref == "main"
    assert len(task.subtasks) == 0


def test_subtask_lifecycle():
    sub = SubTask(
        id="sub-01",
        parent_task_id="task-01",
        title="Atomic Subtask",
        description="Edit files",
        test_command="pytest",
    )
    assert sub.status == TaskStatus.PLANNING
    assert sub.retry_count == 0
    assert sub.max_retries == 3


def test_fleet_event_serialization():
    event = FleetEvent(
        event_id="evt-123",
        event_type=EventType.TASK_STATUS_CHANGED,
        task_id="task-01",
        payload={"status": "working"},
    )
    json_str = event.model_dump_json()
    assert "task.status_changed" in json_str
    assert "evt-123" in json_str
