"""
HTTP & SSE Client for communicating with the Fleet Daemon.
"""

from __future__ import annotations

from typing import Any

import httpx


class FleetClient:
    """Client for Fleet Backend Daemon API."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def health_check(self) -> dict[str, Any]:
        with httpx.Client(base_url=self.base_url, timeout=5.0) as client:
            res = client.get("/api/health")
            res.raise_for_status()
            return res.json()

    def list_tasks(self) -> list[dict[str, Any]]:
        with httpx.Client(base_url=self.base_url, timeout=5.0) as client:
            res = client.get("/api/tasks")
            res.raise_for_status()
            return res.json()

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        with httpx.Client(base_url=self.base_url, timeout=5.0) as client:
            res = client.get(f"/api/tasks/{task_id}")
            if res.status_code == 404:
                return None
            res.raise_for_status()
            return res.json()

    def create_task(self, title: str, prompt: str, base_ref: str = "HEAD") -> dict[str, Any]:
        with httpx.Client(base_url=self.base_url, timeout=10.0) as client:
            res = client.post(
                "/api/tasks",
                json={"title": title, "prompt": prompt, "base_ref": base_ref},
            )
            res.raise_for_status()
            return res.json()

    def list_worktrees(self) -> list[dict[str, str]]:
        with httpx.Client(base_url=self.base_url, timeout=5.0) as client:
            res = client.get("/api/worktrees")
            res.raise_for_status()
            return res.json()
