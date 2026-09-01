"""
LangGraph Worker Harness with Autonomous Self-Healing Validation Loop.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any, TypedDict

from contracts.events import EventType, FleetEvent
from contracts.tasks import SubTask, TaskStatus
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from fleet_backend.harnesses.base import BaseHarness
from fleet_backend.harnesses.tools import WorktreeToolbox

logger = logging.getLogger(__name__)


class WorkerGraphState(TypedDict):
    subtask_id: str
    parent_task_id: str
    title: str
    instruction: str
    worktree_path: str
    target_files: list[str]
    test_command: str | None
    messages: list[BaseMessage]
    iteration: int
    max_retries: int
    test_result: dict[str, Any] | None
    error_feedback: str | None
    status: TaskStatus
    summary: str | None


class LangGraphHarness(BaseHarness):
    """Execution driver that runs a reflective LangGraph loop in an isolated worktree."""

    def __init__(self, llm: BaseChatModel | None = None):
        self.llm = llm
        self._graph = self._build_graph()

    @property
    def name(self) -> str:
        return "langgraph"

    def _build_graph(self) -> Any:
        def inspect_node(state: WorkerGraphState) -> dict[str, Any]:
            toolbox = WorktreeToolbox(state["worktree_path"])
            file_contexts = []
            for file_path in state.get("target_files", []):
                content = toolbox.read_file(file_path)
                file_contexts.append(f"--- File: {file_path} ---\n{content}\n")

            joined_files = (
                "\n".join(file_contexts) if file_contexts else "No specific files pre-selected."
            )
            system_prompt = (
                "You are an autonomous senior software engineer operating inside an isolated Git worktree.\n"
                f"Subtask: {state['title']}\n"
                f"Requirements: {state['instruction']}\n\n"
                f"Workspace Files:\n{joined_files}\n"
            )
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content="Implement the requested code changes."),
            ]
            return {"messages": messages, "iteration": 0, "status": TaskStatus.WORKING}

        def execute_node(state: WorkerGraphState) -> dict[str, Any]:
            iteration = state["iteration"] + 1
            messages = list(state["messages"])
            if state.get("error_feedback"):
                messages.append(
                    HumanMessage(
                        content=(
                            f"Validation failed (Attempt {iteration - 1}):\n"
                            f"{state['error_feedback']}\n\n"
                            "Inspect the errors, adjust the code, and fix the root causes."
                        )
                    )
                )

            if self.llm:
                response = self.llm.invoke(messages)
                messages.append(response)
            else:
                messages.append(
                    AIMessage(content=f"Executed code modifications (Iteration {iteration}).")
                )

            return {"messages": messages, "iteration": iteration}

        def validate_node(state: WorkerGraphState) -> dict[str, Any]:
            test_cmd = state.get("test_command")
            if not test_cmd:
                return {
                    "test_result": {
                        "exit_code": 0,
                        "stdout": "No tests configured.",
                        "stderr": "",
                        "success": True,
                    },
                    "error_feedback": None,
                }

            toolbox = WorktreeToolbox(state["worktree_path"])
            result = toolbox.run_command(test_cmd)

            if not result["success"]:
                err = result["stderr"] or result["stdout"]
                error_feedback = f"Command '{test_cmd}' failed (Exit {result['exit_code']}):\n{err}"
            else:
                error_feedback = None

            return {"test_result": result, "error_feedback": error_feedback}

        def route_validation(state: WorkerGraphState) -> str:
            res = state.get("test_result") or {}
            if res.get("success", False):
                return "finalize_success"
            if state["iteration"] < state["max_retries"]:
                return "execute_changes"
            return "finalize_failure"

        def finalize_success(state: WorkerGraphState) -> dict[str, Any]:
            return {
                "status": TaskStatus.READY_TO_MERGE,
                "summary": f"Completed and verified in {state['iteration']} iteration(s).",
            }

        def finalize_failure(state: WorkerGraphState) -> dict[str, Any]:
            return {
                "status": TaskStatus.NEEDS_REVIEW,
                "summary": f"Failed after {state['iteration']} attempts. Last error: {state.get('error_feedback')}",
            }

        workflow = StateGraph(WorkerGraphState)
        workflow.add_node("inspect", inspect_node)
        workflow.add_node("execute_changes", execute_node)
        workflow.add_node("validate", validate_node)
        workflow.add_node("finalize_success", finalize_success)
        workflow.add_node("finalize_failure", finalize_failure)

        workflow.set_entry_point("inspect")
        workflow.add_edge("inspect", "execute_changes")
        workflow.add_edge("execute_changes", "validate")
        workflow.add_conditional_edges(
            "validate",
            route_validation,
            {
                "execute_changes": "execute_changes",
                "finalize_success": "finalize_success",
                "finalize_failure": "finalize_failure",
            },
        )
        workflow.add_edge("finalize_success", END)
        workflow.add_edge("finalize_failure", END)

        return workflow.compile()

    async def execute(
        self,
        subtask: SubTask,
        worktree_path: Path,
    ) -> AsyncGenerator[FleetEvent, None]:
        """Execute subtask graph and stream events for each step."""
        initial_state: WorkerGraphState = {
            "subtask_id": subtask.id,
            "parent_task_id": subtask.parent_task_id,
            "title": subtask.title,
            "instruction": subtask.description,
            "worktree_path": str(worktree_path),
            "target_files": subtask.target_files,
            "test_command": subtask.test_command,
            "messages": [],
            "iteration": 0,
            "max_retries": subtask.max_retries,
            "test_result": None,
            "error_feedback": None,
            "status": TaskStatus.WORKING,
            "summary": None,
        }

        yield FleetEvent(
            event_id=uuid.uuid4().hex,
            event_type=EventType.SUBTASK_STATUS_CHANGED,
            task_id=subtask.parent_task_id,
            subtask_id=subtask.id,
            payload={"status": TaskStatus.WORKING.value, "title": subtask.title},
        )

        for output in self._graph.stream(initial_state):
            for state_update in output.values():
                if state_update.get("test_result"):
                    yield FleetEvent(
                        event_id=uuid.uuid4().hex,
                        event_type=EventType.TEST_VALIDATION_RESULT,
                        task_id=subtask.parent_task_id,
                        subtask_id=subtask.id,
                        payload=state_update["test_result"],
                    )
                if "status" in state_update:
                    yield FleetEvent(
                        event_id=uuid.uuid4().hex,
                        event_type=EventType.SUBTASK_STATUS_CHANGED,
                        task_id=subtask.parent_task_id,
                        subtask_id=subtask.id,
                        payload={
                            "status": state_update["status"].value
                            if isinstance(state_update["status"], TaskStatus)
                            else state_update["status"],
                            "summary": state_update.get("summary"),
                        },
                    )
