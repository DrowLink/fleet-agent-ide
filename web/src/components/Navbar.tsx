import React from 'react';
import { Bot, GitBranch, Plus, Terminal, Activity, RefreshCw, Cpu, Layers } from 'lucide-react';
import { GitWorktree } from '../types/fleet';

interface NavbarProps {
  isConnected: boolean;
  worktrees: GitWorktree[];
  onOpenNewTask: () => void;
  onToggleTerminal: () => void;
  isTerminalOpen: boolean;
  onRefresh: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  isConnected,
  worktrees,
  onOpenNewTask,
  onToggleTerminal,
  isTerminalOpen,
  onRefresh,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 px-6 py-3.5">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        {/* Left: Brand & Status */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2.5">
            <div className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 shadow-lg shadow-cyan-500/20">
              <Layers className="w-5 h-5 text-white" />
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-rose-400'} opacity-75`}></span>
                <span className={`relative inline-flex rounded-full h-3 w-3 ${isConnected ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
              </span>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-100 via-slate-200 to-cyan-400">
                  Fleet Agent IDE
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-500/30">
                  v0.1.0
                </span>
              </div>
              <p className="text-xs text-slate-400 flex items-center gap-1.5">
                <Activity className="w-3 h-3 text-cyan-400" />
                <span>Worktree Isolation Engine</span>
              </p>
            </div>
          </div>
        </div>

        {/* Center: Worktree & Model Pills */}
        <div className="hidden md:flex items-center space-x-3">
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs text-slate-300">
            <GitBranch className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-400 font-medium">Worktrees:</span>
            <span className="font-bold text-cyan-300">{worktrees.length} active</span>
          </div>

          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-slate-400 font-medium">Runtime:</span>
            <span className="font-semibold text-emerald-300">LangGraph Reflective Loop</span>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onRefresh}
            title="Refresh State"
            className="p-2 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-slate-300 hover:text-white transition-all"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button
            onClick={onToggleTerminal}
            className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-semibold border transition-all ${
              isTerminalOpen
                ? 'bg-cyan-950/60 text-cyan-300 border-cyan-500/40 shadow-sm shadow-cyan-500/20'
                : 'bg-slate-900 text-slate-300 border-slate-800 hover:bg-slate-800'
            }`}
          >
            <Terminal className="w-4 h-4 text-cyan-400" />
            <span>Terminal</span>
          </button>

          <button
            onClick={onOpenNewTask}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white shadow-md shadow-cyan-500/20 hover:shadow-cyan-500/30 transition-all active:scale-95"
          >
            <Plus className="w-4 h-4" />
            <span>New Task Fleet</span>
          </button>
        </div>
      </div>
    </header>
  );
};
