# 🎨 Design System & UI/UX Philosophy (`DESIGN.md`)

This document outlines the visual aesthetics, design principles, and UI tokens used in **Fleet Agent IDE** (Web Dashboard and Terminal Rich CLI).

---

## 🌟 Visual Philosophy

1. **Developer-First Dark Palette**: Deep slate `#070a0f` base inspired by modern high-end IDEs (Linear, Cursor, Raycast).
2. **Glassmorphism & Depth**: Subtle transparent panels with `backdrop-filter: blur(12px)` and delicate 1px border glows.
3. **High-Contrast Telemetry**:
   - 🔵 **Cyan (`#38bdf8`)**: Active operations, worktree branches, system events.
   - 🟢 **Emerald (`#10b981`)**: Passing tests, verified merges, connected SSE streams.
   - 🟡 **Amber (`#f59e0b`)**: Active agent coding iterations and retries.
   - 🔴 **Rose (`#f43f5e`)**: Test tracebacks, failed executions, review alerts.
4. **Fluid Micro-Animations**: Smooth hover transitions, spinning status indicators, and pulsing connection dots.

---

## 🔤 Typography

- **Interface Font**: [Inter](https://fonts.google.com/specimen/Inter) — crisp, high legibility at 11–13px.
- **Code & Terminal Font**: [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) — ligature-enabled, clear distinction of brackets and symbols.

---

## 🧩 Component Architecture

| Component | Purpose | Key Aesthetics |
| :--- | :--- | :--- |
| **`Navbar`** | System telemetry & actions | Glass panel, live pulsing status ring, worktree counter |
| **`KanbanBoard`** | 4-stage fleet state lifecycle | 4 vertical columns with tinted headers and empty-state placeholders |
| **`TaskCard`** | Individual agent task container | Glow on hover, branch badges, attempt counter, quick diff/merge actions |
| **`MonacoDiffModal`** | Side-by-side git diff viewer | Full-screen dark overlay, syntax highlighting, subtask tab switcher |
| **`TerminalStream`** | Real-time test log streamer | Collapsible bottom drawer, timestamped color-coded stream lines |
