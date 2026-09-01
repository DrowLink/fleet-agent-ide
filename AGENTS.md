# 🤖 Agent Guidelines for Fleet Agent IDE (`AGENTS.md`)

This document provides context, conventions, and operational workflows for AI coding agents (Claude Code, Antigravity, Cursor, Aider, OpenHands) contributing to or operating within **Fleet Agent IDE**.

---

## 🏛️ System Topography & Monorepo Layout

`fleet-agent-ide` is a contract-driven monorepo organized into three primary layers:

```text
fleet-agent-ide/
├── contracts/                         # 📜 Pydantic schemas (Task, SubTask, FleetEvent)
│   └── src/contracts/
├── backend/                           # 🧠 FastAPI Daemon, Worktree Manager & LangGraph Harness
│   └── src/fleet_backend/
│       ├── core/                      # worktree_manager.py, db.py, llm_factory.py
│       ├── harnesses/                 # Pluggable execution drivers (langgraph_harness.py)
│       ├── orchestration/             # planner.py, scheduler.py
│       └── api/                       # server.py (FastAPI REST + SSE + WebSockets)
├── cli/                               # 💻 Typer + Rich Terminal Interface
│   └── src/fleet_cli/
│       ├── client.py                  # Daemon HTTP/SSE client
│       └── main.py                    # CLI commands: daemon, run, status, worktrees
└── web/                               # 🖥️ React + Vite + Tailwind Dashboard
    └── src/
        ├── components/                # KanbanBoard, MonacoDiffModal, TerminalStream
        └── hooks/                     # useFleetEvents (SSE subscriber)
```

---

## 🛡️ Core Rules & Invariants for Agents

1. **Strict Zero-Traversal Isolation**:
   - All worker tool executions (file read/write, terminal execution) MUST resolve strictly inside the worker's allocated worktree (`.fleet/worktrees/<task-id>`).
   - Never run modifying commands or writes on the user's active working directory or `main` branch directly.

2. **Contract Consistency**:
   - Whenever adding or changing event types or task attributes, update `contracts/src/contracts/` first.
   - Frontend (`web/src/types/fleet.ts`) and Backend models must stay 100% aligned with contracts.

3. **Pluggable Harness Protocol**:
   - Any new agent execution driver (e.g., Claude Code, Codex, Custom AST Editor) must implement `BaseHarness` in `backend/src/fleet_backend/harnesses/base.py` and yield `FleetEvent` streams.

4. **Self-Healing Validation Loop**:
   - Worker agents must run the designated test command locally.
   - If tests fail (exit code != 0), intercept `stderr`/`stdout`, append the error to history, and iterate up to `max_retries` before marking `NEEDS_REVIEW`.

---

## 🧪 Testing & Verification Commands

```bash
# Backend & Contracts Tests
pytest -v

# Linter & Formatting
ruff check .
ruff format .

# Web Frontend Validation
cd web
npm run build
```
