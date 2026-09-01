"""
Supervisor / Planner Agent for decomposing issues into atomic subtasks.
"""

from __future__ import annotations

import uuid

from contracts.tasks import SubTask, SubTaskPlan, TaskDecomposition, TaskStatus
from langchain_core.language_models import BaseChatModel


class PlannerAgent:
    """Decomposes feature prompts or issues into subtasks with target files and validation commands."""

    def __init__(self, llm: BaseChatModel | None = None):
        self.llm = llm

    def plan_task(self, prompt: str, repo_summary: str = "") -> list[SubTask]:
        parent_id = f"task-{uuid.uuid4().hex[:8]}"

        if self.llm:
            structured_llm = self.llm.with_structured_output(TaskDecomposition)
            system_prompt = (
                "You are the Lead Architect for Fleet Agent IDE.\n"
                "Decompose the given software engineering task into atomic subtasks.\n"
                "Each subtask will execute in its own isolated Git worktree.\n"
                "Specify target files, clear instructions, and validation test commands."
            )
            messages = [
                ("system", system_prompt),
                ("human", f"Repository:\n{repo_summary}\n\nTask:\n{prompt}"),
            ]
            decomposition: TaskDecomposition = structured_llm.invoke(messages)  # type: ignore
            plans = decomposition.subtasks
        else:
            plans = [
                SubTaskPlan(
                    title="Implement Task Changes",
                    description=prompt,
                    target_files=[],
                    test_command="pytest",
                )
            ]

        subtasks: list[SubTask] = []
        for i, p in enumerate(plans):
            subtask = SubTask(
                id=f"{parent_id}-sub-{i + 1}",
                parent_task_id=parent_id,
                title=p.title,
                description=p.description,
                target_files=p.target_files,
                test_command=p.test_command,
                dependencies=p.dependencies,
                status=TaskStatus.PLANNING,
            )
            subtasks.append(subtask)

        return subtasks
