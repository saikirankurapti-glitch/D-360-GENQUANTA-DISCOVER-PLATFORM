import { useState } from 'react';
import { useQueryBuilderStore } from '../store/useQueryBuilderStore';
import { Terminal, Copy, Check, Play, AlertTriangle, Eye, XCircle } from 'lucide-react';

interface SQLPreviewProps {
  onRunQuery: (page: number, pageSize: number) => Promise<void>;
  onExplainPlan: () => Promise<void>;
  onCancelQuery: () => Promise<void>;
  isExecuting: boolean;
  hasActiveQuery: boolean;
}

export const SQLPreview = ({ 
  onRunQuery, 
  onExplainPlan, 
  onCancelQuery, 
  isExecuting, 
  hasActiveQuery 
}: SQLPreviewProps) => {
  const { compiledSQL, validationErrors } = useQueryBuilderStore();
  const [copied, setCopied] = useState(false);
  const [execError, setExecError] = useState<string | null>(null);

  const handleCopy = () => {
    if (!compiledSQL) return;
    navigator.clipboard.writeText(compiledSQL);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRun = async () => {
    setExecError(null);
    try {
      await onRunQuery(1, 5); // default to page 1, page size 5 for demo pagination
    } catch (err: any) {
      setExecError(err.message || 'Execution failed');
    }
  };

  const handleExplain = async () => {
    setExecError(null);
    try {
      await onExplainPlan();
    } catch (err: any) {
      setExecError(err.message || 'Explain plan compilation failed');
    }
  };

  return (
    <div className="glass-panel border border-slate-800 rounded-2xl p-6 flex flex-col h-full space-y-4 shadow-[0_8px_30px_rgba(0,0,0,0.3)]">
      <div className="flex justify-between items-center border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <Terminal className="h-5 w-5 text-sky-400" />
          <h3 className="font-bold text-white text-sm">Trino SQL Preview</h3>
        </div>

        <div className="flex items-center space-x-2">
          {compiledSQL && validationErrors.length === 0 && (
            <>
              <button
                onClick={handleCopy}
                disabled={isExecuting}
                className="flex items-center space-x-1 border border-slate-850 hover:border-slate-800 bg-[#0c1220] hover:bg-[#131b2e] px-2.5 py-1.5 rounded-lg text-[10px] font-bold text-slate-300 transition-colors cursor-pointer disabled:opacity-40"
                title="Copy SQL"
              >
                {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>

              <button
                onClick={handleExplain}
                disabled={isExecuting}
                className="flex items-center space-x-1 border border-slate-850 hover:border-slate-800 bg-[#0c1220] hover:bg-[#131b2e] px-2.5 py-1.5 rounded-lg text-[10px] font-bold text-slate-300 transition-colors cursor-pointer disabled:opacity-40"
                title="Explain Query Plan"
              >
                <Eye className="h-3 w-3 text-sky-400" />
                <span>Explain</span>
              </button>

              {!hasActiveQuery ? (
                <button
                  onClick={handleRun}
                  disabled={isExecuting}
                  className="flex items-center space-x-1 bg-emerald-500 hover:bg-emerald-600 disabled:bg-emerald-700 text-white px-3 py-1.5 rounded-lg text-[10px] font-bold shadow-[0_4px_15px_rgba(16,185,129,0.3)] transition-colors cursor-pointer"
                >
                  <Play className="h-3 w-3 fill-current" />
                  <span>Run Query</span>
                </button>
              ) : (
                <button
                  onClick={onCancelQuery}
                  className="flex items-center space-x-1 bg-rose-500 hover:bg-rose-600 text-white px-3 py-1.5 rounded-lg text-[10px] font-bold shadow-[0_4px_15px_rgba(244,63,94,0.3)] transition-colors cursor-pointer animate-pulse"
                >
                  <XCircle className="h-3 w-3" />
                  <span>Cancel</span>
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {/* Errors Panel */}
      {validationErrors.length > 0 && (
        <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-4 rounded-xl flex items-start space-x-2.5">
          <AlertTriangle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs font-bold uppercase tracking-wider mb-1">Graph Validation Errors</p>
            <ul className="list-disc pl-4 space-y-1 text-xs">
              {validationErrors.map((err, i) => (
                <li key={i}>{err}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {execError && (
        <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-3 rounded-lg text-xs">
          <span>Execution failed: {execError}</span>
        </div>
      )}

      {/* Code Textbox */}
      <div className="flex-1 bg-[#070b13] border border-slate-900 rounded-xl overflow-hidden relative min-h-[120px]">
        {compiledSQL && validationErrors.length === 0 ? (
          <pre className="p-4 text-xs font-mono text-emerald-400 overflow-auto h-full whitespace-pre-wrap leading-relaxed select-text">
            {compiledSQL}
          </pre>
        ) : (
          <div className="h-full flex justify-center items-center text-slate-600 text-xs italic">
            {validationErrors.length > 0
              ? 'Preview unavailable due to graph errors'
              : 'Add entity nodes to canvas to preview SQL'}
          </div>
        )}
      </div>
    </div>
  );
};
