import React, { useEffect, useRef } from 'react';
import { Terminal, Trash2, X, Minimize2, Radio } from 'lucide-react';
import { TerminalLog } from '../hooks/useFleetEvents';

interface TerminalStreamProps {
  isOpen: boolean;
  onClose: () => void;
  logs: TerminalLog[];
  onClear: () => void;
}

export const TerminalStream: React.FC<TerminalStreamProps> = ({
  isOpen,
  onClose,
  logs,
  onClear,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 h-72 glass-panel border-t border-slate-700/80 bg-slate-950/95 shadow-2xl flex flex-col animate-in slide-in-from-bottom duration-200">
      {/* Terminal Header */}
      <div className="flex items-center justify-between px-6 py-2.5 bg-slate-900 border-b border-slate-800">
        <div className="flex items-center space-x-2.5">
          <div className="flex items-center space-x-1.5 px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/30 text-xs font-mono">
            <Radio className="w-3 h-3 animate-pulse text-emerald-400" />
            <span>SSE Live Event & Test Stream</span>
          </div>
          <span className="text-xs text-slate-400">
            {logs.length} events logged
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={onClear}
            title="Clear logs"
            className="p-1 rounded text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-all text-xs flex items-center space-x-1 px-2"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear</span>
          </button>

          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Terminal Content */}
      <div className="flex-1 p-4 overflow-y-auto font-mono text-xs text-slate-300 space-y-1.5 selection:bg-cyan-500/30">
        {logs.length === 0 ? (
          <div className="text-slate-600 italic">No output events logged yet. Execute a task to view real-time agent output...</div>
        ) : (
          logs.map((log) => {
            let color = 'text-slate-300';
            if (log.stream === 'stderr') color = 'text-rose-400 bg-rose-950/20 px-1 py-0.5 rounded';
            if (log.stream === 'system') color = 'text-cyan-400 font-semibold';
            if (log.stream === 'stdout') color = 'text-emerald-300';

            return (
              <div key={log.id} className="leading-relaxed flex items-start space-x-2">
                <span className="text-[10px] text-slate-600 select-none">
                  {log.timestamp.slice(11, 19)}
                </span>
                <span className={`flex-1 whitespace-pre-wrap ${color}`}>
                  {log.text}
                </span>
              </div>
            );
          })
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};
