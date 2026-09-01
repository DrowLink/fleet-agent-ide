# 🌐 Fleet Agent IDE — Technical & Domain Context (`CONTEXT.md`)

## 🎯 The Core Problem

Most AI coding assistants (like Cursor, standard Aider, or ChatGPT) suffer from three structural bottlenecks:

1. **Single-Agent Blocking**: The user must wait for the AI to finish modifying files before starting another task.
2. **Repository & Git Collisions**: If multiple agents run simultaneously on the same working copy, they overwrite each other's files and trigger Git index locks (`.git/index.lock`).
3. **Heavy Virtualization Overhead**: Running full Docker containers or VMs per agent introduces 5–30 second startup times and consumes massive amounts of RAM.

---

## ⚡ The Fleet Solution: Native Git Worktree Isolation

**Fleet Agent IDE** eliminates Docker overhead by leveraging native **Git Worktrees**:

* **Zero-Latency Spawning (<50ms)**: Creating a worktree is an instantaneous filesystem operation that shares the underlying `.git` object store with zero duplication.
* **Complete Process & File Isolation**: Each worker agent operates in `.fleet/worktrees/<task-id>` on its own branch (`agent/<task-id>`), preventing file collisions.
* **Shared Environment Access**: Local Python virtual environments (`.venv`), Node modules, and linters are immediately accessible to all workers.

---

## 🔁 The LangGraph Self-Healing Feedback Loop

Instead of blindly assuming generated code works, Fleet workers run an autonomous test-driven cycle:

```text
[Inspect Target Files]
         │
         ▼
[Apply Code Modifications]
         │
         ▼
[Execute Local Test Command] ── (Exit 0) ──► [READY TO MERGE]
         │
    (Exit != 0)
         │
         ▼
[Parse Traceback & Intercept Stderr]
         │
         ▼ (Iteration < Max Retries)
[Self-Healing Reflection] ───────────────► [Apply Code Modifications]
```

---

## 📡 Real-Time Contract-Driven Observability

Fleet decouples UI clients from the daemon through typed contracts in `contracts/`:
* **SSE (`/api/events/sse`)**: Streams live task progress, test command outputs, and generated git diffs.
* **WebSockets (`/ws/tasks`)**: Bi-directional communication for interactive review and prompt refinement.
* **Persistent SQLite Store**: All task states, retry counts, and error traces survive daemon restarts.
