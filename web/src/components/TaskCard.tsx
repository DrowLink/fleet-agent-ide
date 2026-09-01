import React from 'react';
import { GitBranch, Eye, GitMerge, CheckCircle, Clock, AlertCircle, RefreshCw, Terminal, FileCode } from 'lucide-react';
import { Task, SubTask } from '../types/fleet';

interface TaskCardProps {
  task: Task;
  onOpenDiff: (task: Task) => void;
  onMerge: (task: Task) => void;
  isMerging?: boolean;
}

export const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onOpenDiff,
  onMerge,
  isMerging = false,
}) => {
  const isReadyToMerge = task.status === 'ready_to_merge';
  const isWorking = task.status === 'working';
  const isFailed = task.status === 'failed' || task.status === 'needs_review';
  const isCompleted = task.status === 'completed' || task.status === 'merged';

  const subtask: SubTask | undefined = task.subtasks?.[0];
  const retryCount = subtask?.retry_count || 0;
  const maxRetries = subtask?.max_retries || 3;

  return (
    <div className="glass-card rounded-xl p-4 transition-all duration-200 group relative flex flex-col justify-between">
      <div>
        {/* Top: Status Badge & ID */}
        <div className="flex items-center justify-between mb-2.5">
          <div className="flex items-center space-x-2">
            <span className="text-[11px] font-mono text-cyan-400/80 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-500/20">
              {task.id.length > 16 ? `${task.id.slice(0, 16)}...` : task.id}
            </span>
          </div>

          {isWorking && (
            <span className="flex items-center space-x-1 text-[11px] font-semibold text-amber-400 bg-amber-950/40 px-2 py-0.5 rounded-full border border-amber-500/30">
              <RefreshCw className="w-3 h-3 animate-spin" />
              <span>Working</span>
            </span>
          )}

          {isReadyToMerge && (
            <span className="flex items-center space-x-1 text-[11px] font-semibold text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded-full border border-emerald-500/30">
              <CheckCircle className="w-3 h-3" />
              <span>Ready</span>
            </span>
          )}

          {isFailed && (
            <span className="flex items-center space-x-1 text-[11px] font-semibold text-rose-400 bg-rose-950/40 px-2 py-0.5 rounded-full border border-rose-500/30">
              <AlertCircle className="w-3 h-3" />
              <span>Needs Review</span>
            </span>
          )}

          {isCompleted && (
            <span className="flex items-center space-x-1 text-[11px] font-semibold text-indigo-400 bg-indigo-950/40 px-2 py-0.5 rounded-full border border-indigo-500/30">
              <CheckCircle className="w-3 h-3" />
              <span>Merged</span>
            </span>
          )}
        </div>

        {/* Title & Prompt */}
        <h4 className="font-semibold text-sm text-slate-100 mb-1 line-clamp-1 group-hover:text-cyan-300 transition-colors">
          {task.title || 'Untitled Fleet Task'}
        </h4>
        <p className="text-xs text-slate-400 line-clamp-2 mb-3 leading-relaxed">
          {task.prompt}
        </p>

        {/* Subtask & Branch Info */}
        <div className="space-y-1.5 pt-2 border-t border-slate-800/60 mb-3 text-[11px]">
          {subtask?.branch_name && (
            <div className="flex items-center space-x-1.5 text-slate-300">
              <GitBranch className="w-3.5 h-3.5 text-cyan-400" />
              <span className="font-mono text-slate-300 truncate max-w-[200px]">
                {subtask.branch_name}
              </span>
            </div>
          )}

          {subtask?.test_command && (
            <div className="flex items-center space-x-1.5 text-slate-400">
              <Terminal className="w-3.5 h-3.5 text-emerald-400" />
              <span className="font-mono text-[10px] text-slate-300 bg-slate-900 px-1.5 py-0.5 rounded">
                {subtask.test_command}
              </span>
              {retryCount > 0 && (
                <span className="text-[10px] text-amber-400">
                  (Attempt {retryCount}/{maxRetries})
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="flex items-center gap-2 pt-2 border-t border-slate-800/80">
        <button
          onClick={() => onOpenDiff(task)}
          className="flex-1 flex items-center justify-center space-x-1.5 py-1.5 px-2.5 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-slate-200 text-xs font-medium border border-slate-700/60 hover:border-cyan-500/40 transition-all"
        >
          <Eye className="w-3.5 h-3.5 text-cyan-400" />
          <span>View Diff</span>
        </button>

        {isReadyToMerge && (
          <button
            onClick={() => onMerge(task)}
            disabled={isMerging}
            className="flex-1 flex items-center justify-center space-x-1.5 py-1.5 px-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-sm shadow-emerald-500/30 transition-all active:scale-95 disabled:opacity-50"
          >
            <GitMerge className="w-3.5 h-3.5" />
            <span>{isMerging ? 'Merging...' : 'Merge'}</span>
          </button>
        )}
      </div>
    </div>
  );
};
