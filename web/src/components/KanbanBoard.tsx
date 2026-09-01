import React from 'react';
import { Layers, RefreshCw, CheckCircle2, AlertOctagon, Sparkles } from 'lucide-react';
import { Task } from '../types/fleet';
import { TaskCard } from './TaskCard';

interface KanbanBoardProps {
  tasks: Task[];
  onOpenDiff: (task: Task) => void;
  onMerge: (task: Task) => void;
  mergingTaskId?: string | null;
}

export const KanbanBoard: React.FC<KanbanBoardProps> = ({
  tasks,
  onOpenDiff,
  onMerge,
  mergingTaskId,
}) => {
  const planningTasks = tasks.filter((t) => t.status === 'planning');
  const workingTasks = tasks.filter((t) => t.status === 'working');
  const reviewTasks = tasks.filter(
    (t) => t.status === 'needs_review' || t.status === 'failed'
  );
  const readyTasks = tasks.filter(
    (t) => t.status === 'ready_to_merge' || t.status === 'completed' || t.status === 'merged'
  );

  const columns = [
    {
      id: 'planning',
      title: 'Planning & DAG',
      subtitle: 'Decomposing task',
      icon: Layers,
      color: 'text-cyan-400',
      borderColor: 'border-cyan-500/20',
      badgeBg: 'bg-cyan-950/60 text-cyan-400 border border-cyan-500/30',
      tasks: planningTasks,
    },
    {
      id: 'working',
      title: 'Working in Worktree',
      subtitle: 'Isolated agent coding',
      icon: RefreshCw,
      color: 'text-amber-400',
      borderColor: 'border-amber-500/20',
      badgeBg: 'bg-amber-950/60 text-amber-400 border border-amber-500/30',
      tasks: workingTasks,
      isAnimated: true,
    },
    {
      id: 'review',
      title: 'Self-Correction / Feedback',
      subtitle: 'Retrying failed tests',
      icon: AlertOctagon,
      color: 'text-rose-400',
      borderColor: 'border-rose-500/20',
      badgeBg: 'bg-rose-950/60 text-rose-400 border border-rose-500/30',
      tasks: reviewTasks,
    },
    {
      id: 'ready',
      title: 'Ready to Merge',
      subtitle: 'Tests passed cleanly',
      icon: CheckCircle2,
      color: 'text-emerald-400',
      borderColor: 'border-emerald-500/20',
      badgeBg: 'bg-emerald-950/60 text-emerald-400 border border-emerald-500/30',
      tasks: readyTasks,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
      {columns.map((col) => {
        const Icon = col.icon;
        return (
          <div
            key={col.id}
            className="flex flex-col rounded-2xl glass-panel p-4 min-h-[600px] max-h-[calc(100vh-140px)] border border-slate-800/80"
          >
            {/* Column Header */}
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/60">
              <div className="flex items-center space-x-2.5">
                <div className={`p-1.5 rounded-lg bg-slate-900 border ${col.borderColor}`}>
                  <Icon className={`w-4 h-4 ${col.color} ${col.isAnimated ? 'animate-spin' : ''}`} />
                </div>
                <div>
                  <h3 className="font-semibold text-xs tracking-tight text-slate-200 uppercase">
                    {col.title}
                  </h3>
                  <p className="text-[10px] text-slate-500">{col.subtitle}</p>
                </div>
              </div>
              <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${col.badgeBg}`}>
                {col.tasks.length}
              </span>
            </div>

            {/* Task List */}
            <div className="flex-1 overflow-y-auto space-y-3 pr-1">
              {col.tasks.length === 0 ? (
                <div className="h-40 flex flex-col items-center justify-center text-center p-4 border border-dashed border-slate-800/80 rounded-xl text-slate-600">
                  <Sparkles className="w-6 h-6 mb-2 opacity-30" />
                  <span className="text-xs">No active tasks in this stage</span>
                </div>
              ) : (
                col.tasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onOpenDiff={onOpenDiff}
                    onMerge={onMerge}
                    isMerging={mergingTaskId === task.id}
                  />
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
