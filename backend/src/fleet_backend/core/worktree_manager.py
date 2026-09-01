"""
Git Worktree Isolation Manager for Fleet Backend.

Provides safe, isolated git worktree environments for concurrent agent workers.
Prevents file collisions and git lock contentions while allowing independent
agent execution and branch generation.
"""

from __future__ import annotations

import logging
import os
import shutil
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, List, Optional

import git
from git.exc import GitCommandError, InvalidGitRepositoryError

logger = logging.getLogger(__name__)


class WorktreeManagerError(Exception):
    """Base exception for WorktreeManager operations."""
    pass


class WorktreeCreationError(WorktreeManagerError):
    """Raised when a worktree cannot be created."""
    pass


class WorktreeCleanupError(WorktreeManagerError):
    """Raised when a worktree cannot be removed or cleaned up."""
    pass


@dataclass(frozen=True)
class WorktreeEnvironment:
    """Metadata representing an isolated worktree allocation."""
    task_id: str
    branch_name: str
    worktree_path: Path
    base_commit: str
    repo_root: Path


class WorktreeManager:
    """Manages creation, lifecycle, and teardown of Git worktrees for agent execution."""

    def __init__(
        self,
        repo_path: str | Path,
        worktree_base_dir: Optional[str | Path] = None,
        branch_prefix: str = "agent",
    ) -> None:
        self.repo_path = Path(repo_path).resolve()
        self.branch_prefix = branch_prefix

        if not (self.repo_path / ".git").exists() and not self.repo_path.suffix == ".git":
            raise InvalidGitRepositoryError(f"Directory {self.repo_path} is not a valid Git repository.")

        self.repo = git.Repo(self.repo_path)

        if worktree_base_dir:
            self.worktree_base_dir = Path(worktree_base_dir).resolve()
        else:
            self.worktree_base_dir = self.repo_path / ".fleet" / "worktrees"

        self.worktree_base_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_task_id(self, task_id: str) -> str:
        clean_id = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in task_id)
        return clean_id.strip("_")

    def get_branch_name(self, task_id: str) -> str:
        sanitized = self._sanitize_task_id(task_id)
        return f"{self.branch_prefix}/{sanitized}"

    def get_worktree_path(self, task_id: str) -> Path:
        sanitized = self._sanitize_task_id(task_id)
        return (self.worktree_base_dir / sanitized).resolve()

    def create_worktree(
        self,
        task_id: str,
        base_ref: str = "HEAD",
        force_clean: bool = True,
    ) -> WorktreeEnvironment:
        sanitized_id = self._sanitize_task_id(task_id)
        branch_name = self.get_branch_name(sanitized_id)
        target_path = self.get_worktree_path(sanitized_id)

        if force_clean:
            self.cleanup_worktree(task_id, force=True, delete_branch=False)

        if target_path.exists() and any(target_path.iterdir()):
            raise WorktreeCreationError(f"Target worktree path already exists and is not empty: {target_path}")

        try:
            base_commit = self.repo.commit(base_ref).hexsha

            if branch_name in [h.name for h in self.repo.heads]:
                logger.warning("Branch %s already exists. Deleting it to start clean.", branch_name)
                self.repo.delete_head(branch_name, force=True)

            logger.info("Spawning worktree at '%s' for branch '%s'", target_path, branch_name)
            self.repo.git.worktree("add", "-b", branch_name, str(target_path), base_ref)

            return WorktreeEnvironment(
                task_id=sanitized_id,
                branch_name=branch_name,
                worktree_path=target_path,
                base_commit=base_commit,
                repo_root=self.repo_path,
            )
        except (GitCommandError, Exception) as e:
            logger.error("Failed to create worktree for task %s: %s", task_id, e)
            if target_path.exists():
                shutil.rmtree(target_path, ignore_errors=True)
            self.repo.git.worktree("prune")
            raise WorktreeCreationError(f"Unable to initialize worktree for task {task_id}: {e}") from e

    def cleanup_worktree(
        self,
        task_id: str,
        force: bool = True,
        delete_branch: bool = False,
    ) -> None:
        sanitized_id = self._sanitize_task_id(task_id)
        target_path = self.get_worktree_path(sanitized_id)
        branch_name = self.get_branch_name(sanitized_id)

        try:
            worktrees = self.list_worktrees()
            is_registered = any(Path(wt["path"]).resolve() == target_path for wt in worktrees)

            if is_registered:
                cmd = ["remove"]
                if force:
                    cmd.append("--force")
                cmd.append(str(target_path))
                self.repo.git.worktree(*cmd)

            if target_path.exists():
                shutil.rmtree(target_path, ignore_errors=True)

            self.repo.git.worktree("prune")

            if delete_branch and branch_name in [h.name for h in self.repo.heads]:
                self.repo.delete_head(branch_name, force=True)
                logger.info("Deleted branch %s", branch_name)

        except GitCommandError as e:
            logger.warning("Git warning while cleaning worktree %s: %s", task_id, e)
            if target_path.exists():
                shutil.rmtree(target_path, ignore_errors=True)
            self.repo.git.worktree("prune")
        except Exception as e:
            raise WorktreeCleanupError(f"Failed to cleanup worktree {task_id}: {e}") from e

    def list_worktrees(self) -> List[dict[str, str]]:
        try:
            output = self.repo.git.worktree("list", "--porcelain")
            entries: List[dict[str, str]] = []
            current_entry: dict[str, str] = {}

            for line in output.splitlines():
                if not line.strip():
                    if current_entry:
                        entries.append(current_entry)
                        current_entry = {}
                    continue

                parts = line.split(" ", 1)
                key = parts[0]
                val = parts[1] if len(parts) > 1 else ""

                if key == "worktree":
                    current_entry["path"] = val
                elif key == "HEAD":
                    current_entry["head"] = val
                elif key == "branch":
                    current_entry["branch"] = val.replace("refs/heads/", "")
                elif key == "bare":
                    current_entry["bare"] = "true"
                elif key == "detached":
                    current_entry["detached"] = "true"

            if current_entry:
                entries.append(current_entry)

            return entries
        except Exception as e:
            logger.error("Failed to list worktrees: %s", e)
            return []

    def get_diff(self, task_id: str) -> str:
        """Get git diff of changes made inside the worktree relative to its base."""
        target_path = self.get_worktree_path(task_id)
        if not target_path.exists():
            return ""
        try:
            wt_repo = git.Repo(target_path)
            return wt_repo.git.diff("HEAD~1" if len(wt_repo.iter_commits()) > 1 else "HEAD")
        except Exception:
            try:
                wt_repo = git.Repo(target_path)
                return wt_repo.git.diff()
            except Exception:
                return ""

    @contextmanager
    def session(
        self,
        task_id: str,
        base_ref: str = "HEAD",
        keep_worktree_on_failure: bool = True,
        delete_branch: bool = False,
    ) -> Generator[WorktreeEnvironment, None, None]:
        env = self.create_worktree(task_id=task_id, base_ref=base_ref)
        failed = False
        try:
            yield env
        except Exception:
            failed = True
            raise
        finally:
            if failed and keep_worktree_on_failure:
                logger.warning("Task %s failed. Preserving worktree at '%s'.", task_id, env.worktree_path)
            else:
                self.cleanup_worktree(task_id=task_id, force=True, delete_branch=delete_branch)
