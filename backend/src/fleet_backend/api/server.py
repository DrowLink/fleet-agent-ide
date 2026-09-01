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
