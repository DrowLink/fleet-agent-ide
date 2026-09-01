"""
FastAPI Server & Real-time Task Lifecycle Streaming Daemon.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import AsyncGenerator, Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from contracts.events import FleetEvent, EventType
from contracts.tasks import Task, TaskStatus, SubTask
from fleet_backend.core.db import TaskStore
from fleet_backend.core.worktree_manager import WorktreeManager
from fleet_backend.core.llm_factory import get_llm
from fleet_backend.orchestration.planner import PlannerAgent
from fleet_backend.orchestration.scheduler import FleetScheduler

app = FastAPI(
    title="Fleet Agent IDE Daemon",
    version="0.1.0",
    description="Local Multi-Agent Fleet Orchestrator with Git Worktree Isolation",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateTaskRequest(BaseModel):
    title: str
    prompt: str
    base_ref: str = "HEAD"


class EventBus:
    def __init__(self):
        self._subscribers: list[asyncio.Queue] = []

    async def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        if q in self._subscribers:
            self._subscribers.remove(q)

    async def broadcast(self, event: FleetEvent) -> None:
        for q in list(self._subscribers):
            await q.put(event.model_dump_json())


event_bus = EventBus()
task_store = TaskStore()

try:
    active_llm = get_llm()
except Exception as e:
    active_llm = None

planner = PlannerAgent(llm=active_llm)
worktree_mgr = WorktreeManager(".")
scheduler = FleetScheduler(
    worktree_manager=worktree_mgr,
    task_store=task_store,
    event_callback=event_bus.broadcast,
    llm=active_llm,
)


@app.on_event("startup")
async def on_startup():
    await task_store.initialize()


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "fleet-backend-daemon", "version": "0.1.0"}


@app.get("/api/tasks")
async def list_tasks():
    return await task_store.list_tasks()


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    return await task_store.get_task(task_id)


@app.get("/api/worktrees")
async def list_worktrees():
    return worktree_mgr.list_worktrees()


@app.post("/api/tasks")
async def create_and_run_task(req: CreateTaskRequest, background_tasks: BackgroundTasks):
    """Decomposes a task and schedules its worker fleet in the background."""
    subtasks = planner.plan_task(req.prompt)
    task_id = subtasks[0].parent_task_id if subtasks else f"task-{uuid.uuid4().hex[:8]}"

    task = Task(
        id=task_id,
        title=req.title,
        prompt=req.prompt,
        base_ref=req.base_ref,
        status=TaskStatus.PLANNING,
        subtasks=subtasks,
    )

    await task_store.save_task(task)

    # Dispatch to background scheduler
    background_tasks.add_task(scheduler.run_task_fleet, task)

    return {"task_id": task.id, "subtasks_count": len(subtasks), "status": "scheduled"}


@app.get("/api/tasks/{task_id}/diff")
async def get_task_diff(task_id: str):
    """Retrieve git diffs generated across all subtasks of a task."""
    task_data = await task_store.get_task(task_id)
    if not task_data:
        return {"diff": "", "subtasks_diffs": []}

    subtasks_diffs = []
    combined_diff = []
    for sub in task_data.get("subtasks", []):
        sub_id = sub.get("id")
        diff_content = worktree_mgr.get_diff(sub_id)
        subtasks_diffs.append({
            "subtask_id": sub_id,
            "title": sub.get("title"),
            "branch": sub.get("branch_name"),
            "diff": diff_content,
        })
        if diff_content:
            combined_diff.append(f"# Subtask: {sub.get('title')} ({sub_id})\n{diff_content}")

    return {
        "task_id": task_id,
        "diff": "\n\n".join(combined_diff),
        "subtasks_diffs": subtasks_diffs,
    }


@app.post("/api/tasks/{task_id}/merge")
async def merge_task(task_id: str):
    """Merge all ready subtask branches of a task into main."""
    task_data = await task_store.get_task(task_id)
    if not task_data:
        return {"success": False, "error": "Task not found"}

    results = []
    for sub in task_data.get("subtasks", []):
        branch = sub.get("branch_name")
        if branch:
            res = worktree_mgr.merge_branch(branch, target_branch=task_data.get("base_ref", "main"))
            results.append({"branch": branch, **res})

    all_success = all(r.get("success", False) for r in results)
    if all_success:
        await task_store.update_subtask_status(task_id, TaskStatus.COMPLETED)
        # Broadcast completed status
        await event_bus.broadcast(
            FleetEvent(
                event_id=f"merge-{task_id}",
                event_type=EventType.TASK_STATUS_CHANGED,
                task_id=task_id,
                payload={"status": TaskStatus.COMPLETED.value, "summary": "Successfully merged into main"},
            )
        )

    return {"success": all_success, "details": results}


@app.get("/api/events/sse")
async def sse_event_stream() -> EventSourceResponse:
    """SSE endpoint for live task lifecycle and test feedback events."""
    async def event_generator() -> AsyncGenerator[Dict[str, Any], None]:
        q = await event_bus.subscribe()
        try:
            while True:
                data = await q.get()
                yield {"event": "fleet_event", "data": data}
        except asyncio.CancelledError:
            event_bus.unsubscribe(q)

    return EventSourceResponse(event_generator())


@app.websocket("/ws/tasks")
async def websocket_task_stream(websocket: WebSocket):
    await websocket.accept()
    q = await event_bus.subscribe()
    try:
        while True:
            data = await q.get()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        event_bus.unsubscribe(q)
