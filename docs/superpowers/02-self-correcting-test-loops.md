# ⚡ Superpower: Autonomous Self-Correcting Test Loops

Writing code without verifying it is why many AI agents fail in real production codebases.

With **Fleet Agent IDE**:
1. The Supervisor defines a test verification command (e.g. `pytest tests/test_auth.py`).
2. The Worker makes code changes in its worktree.
3. The Worker executes the test suite locally.
4. If it fails, the agent intercepts `stderr` and traceback details, diagnoses the bug, fixes the files, and re-tests.
5. You only receive a notification when the test suite passes or after exhausting smart retries.
