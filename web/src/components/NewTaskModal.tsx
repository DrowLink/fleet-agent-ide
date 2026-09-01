import React, { useState } from 'react';
import { X, Plus, Sparkles, GitBranch, Cpu } from 'lucide-react';
import { createTask } from '../api/client';

interface NewTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTaskCreated: () => void;
}

export const NewTaskModal: React.FC<NewTaskModalProps> = ({
  isOpen,
  onClose,
  onTaskCreated,
}) => {
  const [title, setTitle] = useState('');
  const [prompt, setPrompt] = useState('');
  const [baseRef, setBaseRef] = useState('HEAD');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    try {
      setLoading(true);
      setError(null);
      await createTask({
        title: title.trim() || 'Autonomous Fleet Task',
        prompt: prompt.trim(),
        base_ref: baseRef || 'HEAD',
      });
      setTitle('');
      setPrompt('');
      onTaskCreated();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to dispatch task');
    } finally {
      setLoading(false);
    }
  };

  const applyTemplate = (tTitle: string, tPrompt: string) => {
    setTitle(tTitle);
    setPrompt(tPrompt);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl rounded-2xl glass-panel border border-slate-700/80 bg-slate-950 shadow-2xl p-6 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 shadow-md shadow-cyan-500/20 text-white">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100">
                Dispatch New Agent Fleet Task
              </h3>
              <p className="text-xs text-slate-400">
                Supervisor will decompose into atomic subtasks in isolated Git worktrees
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Templates */}
        <div className="mb-4">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Quick Templates:
          </span>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() =>
                applyTemplate(
                  'Add Unit Tests',
                  'Add comprehensive pytest unit tests for the worktree manager and state storage.'
                )
              }
              className="text-xs px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-all"
            >
              🧪 Unit Test Suite
            </button>
            <button
              type="button"
              onClick={() =>
                applyTemplate(
                  'API Stats Endpoint',
                  'Create a new endpoint GET /api/stats in FastAPI that returns memory and active worktree telemetry.'
                )
              }
              className="text-xs px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-all"
            >
              ⚡ Stats API Endpoint
            </button>
            <button
              type="button"
              onClick={() =>
                applyTemplate(
                  'Refactor Utilities',
                  'Extract common path resolution and string sanitizers into backend/core/utils.py with type annotations.'
                )
              }
              className="text-xs px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-all"
            >
              ♻️ Refactor Utils
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Task Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Implement JWT Authentication Middleware"
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-100 placeholder:text-slate-600 text-xs focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/40"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Prompt & Requirements <span className="text-cyan-400">*</span>
            </label>
            <textarea
              required
              rows={4}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe what the agent should modify, create, and test..."
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-100 placeholder:text-slate-600 text-xs focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/40 leading-relaxed"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center space-x-1.5">
              <GitBranch className="w-3.5 h-3.5 text-cyan-400" />
              <span>Base Git Reference</span>
            </label>
            <input
              type="text"
              value={baseRef}
              onChange={(e) => setBaseRef(e.target.value)}
              placeholder="HEAD or main"
              className="w-full px-3.5 py-2 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-100 text-xs font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs">
              {error}
            </div>
          )}

          <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-medium border border-slate-800 transition-all"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={loading || !prompt.trim()}
              className="flex items-center space-x-2 px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-cyan-500/20 active:scale-95 disabled:opacity-50 transition-all"
            >
              {loading ? (
                <span>Decomposing DAG...</span>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  <span>Launch Agent Fleet</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
