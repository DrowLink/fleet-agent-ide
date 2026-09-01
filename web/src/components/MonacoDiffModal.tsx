import React, { useEffect, useState } from 'react';
import { X, GitBranch, GitMerge, Check, Copy, FileDiff, Sparkles, Trash2 } from 'lucide-react';
import { DiffEditor } from '@monaco-editor/react';
import { Task, TaskDiffResponse } from '../types/fleet';
import { fetchTaskDiff, mergeTask, deleteTask } from '../api/client';

interface MonacoDiffModalProps {
  task: Task;
  onClose: () => void;
  onMergedSuccess: () => void;
  onDeleteSuccess?: () => void;
}

export const MonacoDiffModal: React.FC<MonacoDiffModalProps> = ({
  task,
  onClose,
  onMergedSuccess,
  onDeleteSuccess,
}) => {
  const [diffData, setDiffData] = useState<TaskDiffResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [isMerging, setIsMerging] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [copied, setCopied] = useState(false);
  const [activeSubtaskIndex, setActiveSubtaskIndex] = useState(0);

  useEffect(() => {
    async function loadDiff() {
      try {
        setLoading(true);
        const data = await fetchTaskDiff(task.id);
        setDiffData(data);
      } catch (err) {
        console.error('Failed to fetch diff:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDiff();
  }, [task.id]);

  const handleMerge = async () => {
    try {
      setIsMerging(true);
      const res = await mergeTask(task.id);
      if (res.success) {
        onMergedSuccess();
        onClose();
      } else {
        alert('Merge error: ' + JSON.stringify(res.details));
      }
    } catch (err) {
      alert('Failed to merge: ' + err);
    } finally {
      setIsMerging(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to discard task "${task.title || task.id}" and remove all isolated worktrees?`)) {
      return;
    }
    try {
      setIsDeleting(true);
      await deleteTask(task.id);
      if (onDeleteSuccess) onDeleteSuccess();
      onClose();
    } catch (err) {
      alert('Failed to delete task: ' + err);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCopyDiff = () => {
    if (diffData?.diff) {
      navigator.clipboard.writeText(diffData.diff);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const currentSubtaskDiff = diffData?.subtasks_diffs?.[activeSubtaskIndex];
  const activeDiffContent = currentSubtaskDiff?.diff || diffData?.diff || 'No diff changes generated yet.';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-6xl h-[85vh] flex flex-col rounded-2xl glass-panel border border-slate-700/80 bg-slate-950 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/60">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-cyan-950/60 text-cyan-400 border border-cyan-500/30">
              <FileDiff className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-semibold text-slate-100">
                  {task.title || 'Task Git Diff'}
                </h3>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  {task.id}
                </span>
              </div>
              <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
                <GitBranch className="w-3.5 h-3.5 text-cyan-400" />
                <span>Base: <b className="text-slate-200">{task.base_ref}</b></span>
                {currentSubtaskDiff?.branch && (
                  <span>→ Agent Branch: <b className="text-cyan-300 font-mono">{currentSubtaskDiff.branch}</b></span>
                )}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleCopyDiff}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-all"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Diff'}</span>
            </button>

            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-rose-950/60 hover:bg-rose-900/80 text-rose-300 text-xs font-medium border border-rose-500/30 transition-all disabled:opacity-50"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>{isDeleting ? 'Discarding...' : 'Discard Task'}</span>
            </button>

            {task.status === 'ready_to_merge' && (
              <button
                onClick={handleMerge}
                disabled={isMerging}
                className="flex items-center space-x-1.5 px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-500/20 transition-all active:scale-95 disabled:opacity-50"
              >
                <GitMerge className="w-3.5 h-3.5" />
                <span>{isMerging ? 'Merging...' : 'Merge to Main'}</span>
              </button>
            )}

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Subtask Tabs if multiple */}
        {diffData?.subtasks_diffs && diffData.subtasks_diffs.length > 1 && (
          <div className="flex items-center space-x-2 px-6 py-2 border-b border-slate-800 bg-slate-900/40 overflow-x-auto">
            {diffData.subtasks_diffs.map((sub, idx) => (
              <button
                key={sub.subtask_id}
                onClick={() => setActiveSubtaskIndex(idx)}
                className={`px-3 py-1 text-xs rounded-lg font-medium transition-all ${
                  activeSubtaskIndex === idx
                    ? 'bg-cyan-950/80 text-cyan-300 border border-cyan-500/40 shadow-sm'
                    : 'text-slate-400 hover:bg-slate-800'
                }`}
              >
                Subtask: {sub.title}
              </button>
            ))}
          </div>
        )}

        {/* Monaco Diff Content */}
        <div className="flex-1 relative bg-[#1e1e1e]">
          {loading ? (
            <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-sm">
              <Sparkles className="w-5 h-5 animate-spin mr-2 text-cyan-400" />
              Loading worktree diff from Git...
            </div>
          ) : (
            <div className="w-full h-full p-4 overflow-auto font-mono text-xs text-slate-200">
              <pre className="whitespace-pre-wrap leading-relaxed">
                {activeDiffContent.split('\n').map((line, i) => {
                  let colorClass = 'text-slate-300';
                  if (line.startsWith('+') && !line.startsWith('+++')) {
                    colorClass = 'text-emerald-400 bg-emerald-950/30 px-1 rounded block';
                  } else if (line.startsWith('-') && !line.startsWith('---')) {
                    colorClass = 'text-rose-400 bg-rose-950/30 px-1 rounded block';
                  } else if (line.startsWith('@@')) {
                    colorClass = 'text-cyan-400 font-bold block my-1';
                  } else if (line.startsWith('diff --git')) {
                    colorClass = 'text-yellow-400 font-bold block mt-3 pb-1 border-b border-slate-800';
                  }
                  return (
                    <span key={i} className={colorClass}>
                      {line || ' '}
                    </span>
                  );
                })}
              </pre>
            </div>
          )}
        </div>

        {/* Footer info */}
        <div className="px-6 py-2.5 bg-slate-900 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
          <span>Git Worktree changes isolated from main repository</span>
          <span className="font-mono text-cyan-400">Ready for review</span>
        </div>
      </div>
    </div>
  );
};
