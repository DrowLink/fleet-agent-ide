"""SQLite State Persistence Manager for Fleet Agent IDE."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional
import aiosqlite
from contracts.tasks import Task, SubTask, TaskStatus


class TaskStore:
    """Asynchronous SQLite persistence for tasks and subtasks."""

    def __init__(self, db_path: str | Path = ".fleet/fleet_state.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self) -> None:
        """Create tables if they do not exist."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    base_ref TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS subtasks (
                    id TEXT PRIMARY KEY,
                    parent_task_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    target_files_json TEXT,
                    test_command TEXT,
                    dependencies_json TEXT,
                    status TEXT NOT NULL,
                    assigned_harness TEXT,
                    assigned_worker_id TEXT,
                    worktree_path TEXT,
                    branch_name TEXT,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    error_log TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(parent_task_id) REFERENCES tasks(id)
                )
            """)
            await db.commit()

    async def save_task(self, task: Task) -> None:
        """Upsert a task and its subtasks."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO tasks (id, title, prompt, base_ref, status, metadata_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.id,
                    task.title,
                    task.prompt,
                    task.base_ref,
                    task.status.value,
                    json.dumps(task.metadata),
                    task.created_at.isoformat(),
                    task.updated_at.isoformat(),
                ),
            )
            for sub in task.subtasks:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO subtasks (
                        id, parent_task_id, title, description, target_files_json,
                        test_command, dependencies_json, status, assigned_harness,
                        assigned_worker_id, worktree_path, branch_name,
                        retry_count, max_retries, error_log, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sub.id,
                        sub.parent_task_id,
                        sub.title,
                        sub.description,
                        json.dumps(sub.target_files),
                        sub.test_command,
                        json.dumps(sub.dependencies),
                        sub.status.value,
                        sub.assigned_harness,
                        sub.assigned_worker_id,
                        sub.worktree_path,
                        sub.branch_name,
                        sub.retry_count,
                        sub.max_retries,
                        sub.error_log,
                        sub.created_at.isoformat(),
                        sub.updated_at.isoformat(),
                    ),
                )
            await db.commit()

    async def update_subtask_status(
        self,
        subtask_id: str,
        status: TaskStatus,
        error_log: Optional[str] = None,
        retry_count: Optional[int] = None,
    ) -> None:
        """Update status and retry info for a subtask."""
        async with aiosqlite.connect(self.db_path) as db:
            if retry_count is not None:
                await db.execute(
                    """
                    UPDATE subtasks
                    SET status = ?, error_log = ?, retry_count = ?, updated_at = datetime('now')
                    WHERE id = ?
                    """,
                    (status.value, error_log, retry_count, subtask_id),
                )
            else:
                await db.execute(
                    """
                    UPDATE subtasks
                    SET status = ?, error_log = ?, updated_at = datetime('now')
                    WHERE id = ?
                    """,
                    (status.value, error_log, subtask_id),
                )
            await db.commit()

    async def list_tasks(self) -> List[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_task(self, task_id: str) -> Optional[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            task_dict = dict(row)
            sub_cursor = await db.execute("SELECT * FROM subtasks WHERE parent_task_id = ?", (task_id,))
            sub_rows = await sub_cursor.fetchall()
            task_dict["subtasks"] = [dict(s) for s in sub_rows]
            return task_dict
