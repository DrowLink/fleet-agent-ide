# 🏛️ Fleet Agent IDE Architecture

`fleet-agent-ide` is a local multi-agent code orchestration platform engineered to execute parallel agent fleets with zero repository conflicts and native self-correction.

---

## 🧩 System Topography

```mermaid
graph TD
    Client["💻 Client (CLI / Web / IDE Plugin)"] <-->|REST + SSE / WebSocket| Daemon["⚡ Fleet Backend Daemon (FastAPI)"]
    
    subgraph Core Engine
        Daemon <--> State["💾 Async SQLite Store (contracts/tasks.py)"]
        Daemon --> Scheduler["⚙️ Fleet Scheduler & DAG Resolver"]
        Scheduler --> Planner["🧠 Supervisor / Planner (LangGraph)"]
        Scheduler --> WorktreeMgr["🛡️ Git Worktree Isolation Engine"]
    end
    
    subgraph Agent Execution Runtimes (Harnesses)
        WorktreeMgr -->|Spawn agent/task-1| WT1["📁 Worktree 1 (.fleet/worktrees/sub-1)"]
        WorktreeMgr -->|Spawn agent/task-2| WT2["📁 Worktree 2 (.fleet/worktrees/sub-2)"]
        
        WT1 --> H1["🤖 LangGraph Harness"]
        WT2 --> H2["🤖 Pluggable Harness (Claude / Custom)"]
        
        H1 --> V1{"🧪 Automated Test Loop"}
        V1 -- "Exit code != 0" --> Fix1["🔁 Self-Healing Reflection"]
        Fix1 --> H1
        V1 -- "Exit code == 0" --> Ready1["✅ Ready to Merge"]
    end
```

---

## 📦 Layered Decomposition

### 1. Contract Layer (`contracts/`)
The single source of truth for schemas across client and daemon:
- **Task & DAG Contracts**: Defines `Task`, `SubTask`, `TaskStatus`, and execution dependencies.
- **Streaming Event Contracts**: Standard envelopes for SSE / WebSocket real-time events (`DIFF_GENERATED`, `TEST_VALIDATION_RESULT`, `SUBTASK_STATUS_CHANGED`).
- **Harness Protocol**: Strict Python typing protocol defining how any agent execution engine hooks into Fleet worktrees.

### 2. Backend Daemon (`backend/`)
- **FastAPI Daemon**: Asynchronous background service exposing endpoints and streaming event queues.
- **Git Worktree Manager**: Low-latency local isolation manager provisioning independent Git working trees and automatic branches (`agent/<task-id>`).
- **Orchestration & Schedulers**: Decomposes high-level prompts into atomic subtasks and schedules them concurrently.

### 3. Harness Layer (`backend/harnesses/`)
- Encapsulates agent logic from workspace isolation.
- **LangGraph Worker Harness**: State graph executing atomic file operations, running automated validations (`pytest`, `ruff`), and feeding back `stderr` in a reflection cycle.

### 4. Interactive CLI (`cli/`)
- Built with **Typer** and **Rich** for human-first developer workflows in the terminal.
