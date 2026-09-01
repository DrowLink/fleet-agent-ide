import { useEffect, useState, useCallback, useRef } from 'react';
import { Task, FleetEvent, GitWorktree } from '../types/fleet';
import { fetchTasks, fetchWorktrees, fetchHealth } from '../api/client';

export interface TerminalLog {
  id: string;
  timestamp: string;
  subtaskId?: string;
  taskId: string;
  stream: 'stdout' | 'stderr' | 'system';
  text: string;
}

export function useFleetEvents() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [worktrees, setWorktrees] = useState<GitWorktree[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [logs, setLogs] = useState<TerminalLog[]>([]);
  const [loading, setLoading] = useState(true);
  const eventSourceRef = useRef<EventSource | null>(null);

  const refreshData = useCallback(async () => {
    try {
      const [fetchedTasks, fetchedWorktrees] = await Promise.all([
        fetchTasks(),
        fetchWorktrees().catch(() => []),
      ]);
      setTasks(fetchedTasks);
      setWorktrees(fetchedWorktrees);
      setIsConnected(true);
    } catch (err) {
      console.warn('Backend fetch error:', err);
      setIsConnected(false);
    } finally {
      setLoading(false);
    }
  }, []);

  const appendLog = useCallback((log: TerminalLog) => {
    setLogs((prev) => [...prev.slice(-400), log]);
  }, []);

  useEffect(() => {
    // Initial load
    refreshData();

    // Setup SSE stream
    const sseUrl = '/api/events/sse';
    const es = new EventSource(sseUrl);
    eventSourceRef.current = es;

    es.onopen = () => {
      setIsConnected(true);
      appendLog({
        id: Math.random().toString(),
        timestamp: new Date().toISOString(),
        taskId: 'system',
        stream: 'system',
        text: '⚡ Connected to Fleet Agent IDE Daemon Event Stream (SSE).',
      });
    };

    es.addEventListener('fleet_event', (e: MessageEvent) => {
      try {
        const rawEvent = typeof e.data === 'string' ? JSON.parse(e.data) : e.data;
        const fleetEvent: FleetEvent = typeof rawEvent === 'string' ? JSON.parse(rawEvent) : rawEvent;

        // Log to terminal stream
        if (fleetEvent.event_type === 'subtask.status_changed') {
          appendLog({
            id: fleetEvent.event_id,
            timestamp: fleetEvent.timestamp,
            taskId: fleetEvent.task_id,
            subtaskId: fleetEvent.subtask_id,
            stream: 'system',
            text: `[STATUS] Subtask ${fleetEvent.subtask_id} -> ${fleetEvent.payload?.status || 'updated'} ${
              fleetEvent.payload?.summary ? `(${fleetEvent.payload.summary})` : ''
            }`,
          });
        } else if (fleetEvent.event_type === 'test.validation_result') {
          const success = fleetEvent.payload?.success;
          appendLog({
            id: fleetEvent.event_id,
            timestamp: fleetEvent.timestamp,
            taskId: fleetEvent.task_id,
            subtaskId: fleetEvent.subtask_id,
            stream: success ? 'stdout' : 'stderr',
            text: `[TEST] Exit code: ${fleetEvent.payload?.exit_code}\n${
              fleetEvent.payload?.stdout || fleetEvent.payload?.stderr || ''
            }`,
          });
        } else if (fleetEvent.event_type === 'diff.generated') {
          appendLog({
            id: fleetEvent.event_id,
            timestamp: fleetEvent.timestamp,
            taskId: fleetEvent.task_id,
            subtaskId: fleetEvent.subtask_id,
            stream: 'system',
            text: `[GIT] Worktree branch ${fleetEvent.payload?.branch} generated diff.`,
          });
        }

        // Refresh state
        refreshData();
      } catch (err) {
        console.error('Failed to parse SSE event:', err);
      }
    });

    es.onerror = () => {
      setIsConnected(false);
    };

    // Polling backup interval every 4s
    const interval = setInterval(refreshData, 4000);

    return () => {
      es.close();
      clearInterval(interval);
    };
  }, [refreshData, appendLog]);

  return {
    tasks,
    worktrees,
    isConnected,
    logs,
    loading,
    refreshData,
    appendLog,
  };
}
