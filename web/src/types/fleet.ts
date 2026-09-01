export type TaskStatus =
  | 'planning'
  | 'working'
  | 'needs_review'
  | 'ready_to_merge'
  | 'merged'
  | 'failed'
  | 'completed';

export interface SubTask {
  id: string;
  parent_task_id: string;
  title: string;
  description: string;
  target_files?: string[] | string;
  test_command?: string | null;
  status: TaskStatus;
  assigned_harness?: string;
  assigned_worker_id?: string | null;
  worktree_path?: string | null;
  branch_name?: string | null;
  retry_count: number;
  max_retries: number;
  error_log?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  title: string;
  prompt: string;
  base_ref: string;
  status: TaskStatus;
  subtasks: SubTask[];
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface GitWorktree {
  path: string;
  branch?: string;
  head?: string;
}

export interface FleetEvent {
  event_id: string;
  event_type: string;
  timestamp: string;
  task_id: string;
  subtask_id?: string;
  payload: Record<string, any>;
}

export interface SubtaskDiff {
  subtask_id: string;
  title: string;
  branch: string;
  diff: string;
}

export interface TaskDiffResponse {
  task_id: string;
  diff: string;
  subtasks_diffs: SubtaskDiff[];
}
