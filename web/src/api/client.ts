import { Task, GitWorktree, TaskDiffResponse } from '../types/fleet';

const API_BASE = '/api';

export async function fetchHealth(): Promise<{ status: string; service: string }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Daemon unreachable');
  return res.json();
}

export async function fetchTasks(): Promise<Task[]> {
  const res = await fetch(`${API_BASE}/tasks`);
  if (!res.ok) throw new Error('Failed to load tasks');
  const tasks = await res.json();
  
  // Also fetch subtasks for each task to display rich cards
  const fullTasks = await Promise.all(
    tasks.map(async (t: any) => {
      try {
        const subRes = await fetch(`${API_BASE}/tasks/${t.id}`);
        if (subRes.ok) {
          const detail = await subRes.json();
          return {
            ...t,
            subtasks: detail.subtasks || [],
          };
        }
      } catch {
        // fallback
      }
      return { ...t, subtasks: [] };
    })
  );

  return fullTasks;
}

export async function fetchWorktrees(): Promise<GitWorktree[]> {
  const res = await fetch(`${API_BASE}/worktrees`);
  if (!res.ok) throw new Error('Failed to load worktrees');
  return res.json();
}

export async function createTask(payload: {
  title: string;
  prompt: string;
  base_ref?: string;
}): Promise<{ task_id: string; subtasks_count: number }> {
  const res = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to create task');
  return res.json();
}

export async function fetchTaskDiff(taskId: string): Promise<TaskDiffResponse> {
  const res = await fetch(`${API_BASE}/tasks/${taskId}/diff`);
  if (!res.ok) throw new Error('Failed to fetch diff');
  return res.json();
}

export async function mergeTask(taskId: string): Promise<{ success: boolean; details: any[] }> {
  const res = await fetch(`${API_BASE}/tasks/${taskId}/merge`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to merge task');
  return res.json();
}
