# ADR 0001: Git Worktree Isolation vs Containerization

## Context
Running multiple AI coding agents concurrently in the same local repository leads to race conditions, dirty file overrides, and git lock contention (`.git/index.lock`).

## Decision
We utilize native **Git Worktrees** (`git worktree add / remove / prune`) stored under `.fleet/worktrees/<task-id>` linked to automatic branches (`agent/<task-id>`).

## Consequences
- **Positive**: Zero container overhead, instant filesystem checkout (<50ms), shares local `.git` objects without cloning, native access to local dependencies (venv, node_modules).
- **Negative**: Requires disk space for checked-out working trees; requires robust cleanup routines on process failure or unhandled exceptions.
