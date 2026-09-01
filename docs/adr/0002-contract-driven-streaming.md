# ADR 0002: Contract-Driven Architecture & Real-Time Event Streaming

## Context
Multiple interfaces (CLI, Web UI, Desktop apps) need real-time awareness of agent state, test execution outputs, and git diff generation without tight coupling to the backend daemon.

## Decision
We decouple all boundaries using strongly-typed Pydantic contracts in `contracts/` and stream lifecycle events over **Server-Sent Events (SSE)** and **WebSockets**.

## Consequences
- **Positive**: Single source of truth for schemas across Python backend and TypeScript/React frontends; easy telemetry and observability.
- **Negative**: Requires maintaining backward compatibility in event contracts.
