import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { KanbanBoard } from './components/KanbanBoard';
import { MonacoDiffModal } from './components/MonacoDiffModal';
import { TerminalStream } from './components/TerminalStream';
import { NewTaskModal } from './components/NewTaskModal';
import { useFleetEvents } from './hooks/useFleetEvents';
import { Task } from './types/fleet';
import { mergeTask } from './api/client';
import { GitBranch, Layers, CheckCircle2, RefreshCw, Zap, Sparkles } from 'lucide-react';

export function App() {
  const { tasks, worktrees, isConnected, logs, loading, refreshData, appendLog } = useFleetEvents();
  const [selectedDiffTask, setSelectedDiffTask] = useState<Task | null>(null);
  const [isNewTaskModalOpen, setIsNewTaskModalOpen] = useState(false);
  const [isTerminalOpen, setIsTerminalOpen] = useState(true);
  const [mergingTaskId, setMergingTaskId] = useState<string | null>(null);

  const handleMerge = async (task: Task) => {
    try {
      setMergingTaskId(task.id);
      const res = await mergeTask(task.id);
      if (res.success) {
        appendLog({
          id: Math.random().toString(),
          timestamp: new Date().toISOString(),
          taskId: task.id,
          stream: 'system',
          text: `🎉 Merged task ${task.id} branches into main successfully!`,
        });
        refreshData();
      } else {
        alert('Merge error: ' + JSON.stringify(res.details));
      }
    } catch (err: any) {
      alert('Failed to merge: ' + err.message);
    } finally {
      setMergingTaskId(null);
    }
  };

  const completedCount = tasks.filter((t) => t.status === 'completed' || t.status === 'merged').length;
  const workingCount = tasks.filter((t) => t.status === 'working').length;
  const readyCount = tasks.filter((t) => t.status === 'ready_to_merge').length;

  return (
    <div className="min-h-screen flex flex-col bg-[#070a0f] text-slate-100 selection:bg-cyan-500/30">
      {/* Top Navigation */}
      <Navbar
        isConnected={isConnected}
        worktrees={worktrees}
        onOpenNewTask={() => setIsNewTaskModalOpen(true)}
        onToggleTerminal={() => setIsTerminalOpen(!isTerminalOpen)}
        isTerminalOpen={isTerminalOpen}
        onRefresh={refreshData}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-6 space-y-6">
        {/* Metric Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-xl border border-slate-800/80 flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-cyan-950/60 text-cyan-400 border border-cyan-500/20">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[11px] font-medium text-slate-400 block">Total Tasks</span>
              <span className="text-lg font-bold text-slate-100">{tasks.length}</span>
            </div>
          </div>

          <div className="glass-panel p-4 rounded-xl border border-slate-800/80 flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-amber-950/60 text-amber-400 border border-amber-500/20">
              <RefreshCw className="w-5 h-5 animate-spin-slow" />
            </div>
            <div>
              <span className="text-[11px] font-medium text-slate-400 block">Working Fleets</span>
              <span className="text-lg font-bold text-amber-300">{workingCount}</span>
            </div>
          </div>

          <div className="glass-panel p-4 rounded-xl border border-slate-800/80 flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-emerald-950/60 text-emerald-400 border border-emerald-500/20">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[11px] font-medium text-slate-400 block">Ready to Merge</span>
              <span className="text-lg font-bold text-emerald-300">{readyCount}</span>
            </div>
          </div>

          <div className="glass-panel p-4 rounded-xl border border-slate-800/80 flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-indigo-950/60 text-indigo-400 border border-indigo-500/20">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[11px] font-medium text-slate-400 block">Merged Changes</span>
              <span className="text-lg font-bold text-indigo-300">{completedCount}</span>
            </div>
          </div>
        </div>

        {/* Multi-Agent Kanban Board */}
        <section>
          <KanbanBoard
            tasks={tasks}
            onOpenDiff={(task) => setSelectedDiffTask(task)}
            onMerge={handleMerge}
            mergingTaskId={mergingTaskId}
          />
        </section>
      </main>

      {/* Terminal Streamer Drawer */}
      <TerminalStream
        isOpen={isTerminalOpen}
        onClose={() => setIsTerminalOpen(false)}
        logs={logs}
        onClear={() => {}}
      />

      {/* Monaco Diff Modal */}
      {selectedDiffTask && (
        <MonacoDiffModal
          task={selectedDiffTask}
          onClose={() => setSelectedDiffTask(null)}
          onMergedSuccess={() => {
            refreshData();
            setSelectedDiffTask(null);
          }}
        />
      )}

      {/* New Task Modal */}
      <NewTaskModal
        isOpen={isNewTaskModalOpen}
        onClose={() => setIsNewTaskModalOpen(false)}
        onTaskCreated={refreshData}
      />
    </div>
  );
}

export default App;
