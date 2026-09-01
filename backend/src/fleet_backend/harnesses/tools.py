"""
Worktree-scoped execution tools for Worker agents.
Ensures zero path traversal outside the allocated worktree.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Dict, Any


class WorktreeToolbox:
    """Factory for creating tools bound strictly to a specific worktree directory."""

    def __init__(self, worktree_path: str | Path):
        self.worktree_path = Path(worktree_path).resolve()
        if not self.worktree_path.exists():
            raise FileNotFoundError(f"Worktree directory {self.worktree_path} does not exist.")

    def _resolve_safe_path(self, rel_or_abs_path: str) -> Path:
        target = (self.worktree_path / rel_or_abs_path).resolve()
        if not str(target).startswith(str(self.worktree_path)):
            raise PermissionError(f"Access denied: path '{rel_or_abs_path}' escapes worktree root.")
        return target

    def read_file(self, file_path: str) -> str:
        path = self._resolve_safe_path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' does not exist."
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            return f"Error reading file '{file_path}': {e}"

    def write_file(self, file_path: str, content: str) -> str:
        path = self._resolve_safe_path(file_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return f"Successfully wrote {len(content)} bytes to '{file_path}'."
        except Exception as e:
            return f"Error writing file '{file_path}': {e}"

    def run_command(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        """Run tests/linters in the worktree directory."""
        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=str(self.worktree_path),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "success": proc.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s.",
                "success": False,
            }
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Execution error: {e}",
                "success": False,
            }
