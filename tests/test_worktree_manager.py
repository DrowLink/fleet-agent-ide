"""Unit tests for WorktreeManager."""

from pathlib import Path

from fleet_backend.core.worktree_manager import WorktreeManager


def test_worktree_manager_initialization():
    mgr = WorktreeManager(".")
    assert mgr.repo_path == Path(".").resolve()
    assert mgr.branch_prefix == "agent"
    assert mgr.worktree_base_dir.exists()


def test_worktree_branch_name():
    mgr = WorktreeManager(".")
    branch = mgr.get_branch_name("task-123-abc")
    assert branch == "agent/task-123-abc"


def test_worktree_list():
    mgr = WorktreeManager(".")
    wts = mgr.list_worktrees()
    assert isinstance(wts, list)
    assert len(wts) >= 1  # Main repo is at least one worktree
