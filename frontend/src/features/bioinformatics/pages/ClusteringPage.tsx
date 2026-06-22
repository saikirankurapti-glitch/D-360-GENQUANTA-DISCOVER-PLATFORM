import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../../services/api';
import _createPlotlyComponent from 'react-plotly.js/factory';
import Plotly from 'plotly.js-dist-min';

const createPlotlyComponent = typeof _createPlotlyComponent === 'function'
  ? _createPlotlyComponent
  : (_createPlotlyComponent as any).default;

const Plot = createPlotlyComponent(Plotly);
import { GitMerge, Settings, CheckCircle } from 'lucide-react';

export const ClusteringPage: React.FC = () => {
  const [sequences, setSequences] = useState<any[]>([]);
  const [selectedMsaIds, setSelectedMsaIds] = useState<string[]>([]);
  const [clusterName, setClusterName] = useState('My Clustering Run');
  const [method, setMethod] = useState('UPGMA');
  const [metric, setMetric] = useState('identity');
  
  const [clusteringResult, setClusteringResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSequences = async () => {
    try {
      const data = await apiRequest('/sequences', { service: 'bioinformatics' });
      setSequences(data);
    } catch (err) {
      console.error('Failed to load sequences', err);
    }
  };

  useEffect(() => {
    fetchSequences();
  }, []);

  const handleRunClustering = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedMsaIds.length < 2) {
      setError('Select at least 2 sequences to compute clustering.');
      return;
    }
    setError(null);
    setIsLoading(true);
    setClusteringResult(null);

    const payload = {
      name: clusterName,
      seq_ids: selectedMsaIds,
      method: method,
      distance_metric: metric
    };

    try {
      const res = await apiRequest('/clusters', {
        service: 'bioinformatics',
        method: 'POST',
        body: JSON.stringify(payload)
      });
      setClusteringResult(res);
    } catch (err: any) {
      setError(err.message || 'Clustering execution failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSelect = (id: string) => {
    setSelectedMsaIds((prev) => 
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const getHeatmapData = () => {
    if (!clusteringResult || !clusteringResult.matrix_json) return [];
    const matrix = JSON.parse(clusteringResult.matrix_json);
    return [
      {
        z: matrix.values,
        x: matrix.labels,
        y: matrix.labels,
        type: 'heatmap' as const,
        colorscale: 'Viridis' as const,
        reversescale: true
      }
    ];
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto py-2 text-slate-100">
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Setup */}
        <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-2xl backdrop-blur-md space-y-4">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Settings className="w-4 h-4 text-blue-400" />
            Clustering Parameters
          </h3>
          
          {error && (
            <div className="p-2.5 bg-red-500/10 border border-red-500/25 text-red-300 rounded-xl text-[11px]">
              {error}
            </div>
          )}

          <form onSubmit={handleRunClustering} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-400 font-semibold mb-1 uppercase tracking-wider">Analysis Label</label>
              <input
                type="text"
                value={clusterName}
                onChange={(e) => setClusterName(e.target.value)}
                className="w-full bg-slate-850 border border-slate-700/60 rounded-lg p-2.5 text-slate-100 outline-none focus:border-blue-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-400 font-semibold mb-1 uppercase tracking-wider">Method</label>
                <select
                  value={method}
                  onChange={(e) => setMethod(e.target.value)}
                  className="w-full bg-slate-850 border border-slate-700/60 rounded-lg p-2 text-slate-100 outline-none"
                >
                  <option value="UPGMA">UPGMA (Average)</option>
                  <option value="single">Single Linkage</option>
                  <option value="complete">Complete Linkage</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-400 font-semibold mb-1 uppercase tracking-wider">Distance Metric</label>
                <select
                  value={metric}
                  onChange={(e) => setMetric(e.target.value)}
                  className="w-full bg-slate-850 border border-slate-700/60 rounded-lg p-2 text-slate-100 outline-none"
                >
                  <option value="identity">1 - Alignment Identity</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-2 uppercase tracking-wider">Select Seqs ({selectedMsaIds.length})</label>
              <div className="space-y-2 max-h-[200px] overflow-y-auto pr-1">
                {sequences.map((s) => {
                  const checked = selectedMsaIds.includes(s.sequence_id);
                  return (
                    <button
                      type="button"
                      key={s.sequence_id}
                      onClick={() => toggleSelect(s.sequence_id)}
                      className={`w-full text-left p-2.5 rounded-xl border transition-all flex items-center gap-3 ${checked ? 'bg-blue-500/10 border-blue-500/40 text-blue-300' : 'bg-slate-800/25 border-slate-700/40 text-slate-400 hover:bg-slate-850'}`}
                    >
                      <div className={`w-4 h-4 rounded border flex items-center justify-center ${checked ? 'bg-blue-600 border-blue-500 text-white' : 'border-slate-600'}`}>
                        {checked && <CheckCircle className="w-3 h-3 fill-current" />}
                      </div>
                      <div className="overflow-hidden">
                        <div className="font-bold text-slate-200 truncate">{s.name}</div>
                        <div className="text-[9px] text-slate-500 truncate font-mono mt-0.5">{s.sequence_id}</div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading || selectedMsaIds.length < 2}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed font-bold rounded-xl transition-all shadow-lg"
            >
              {isLoading ? 'Clustering...' : 'Execute Hierarchical Clustering'}
            </button>
          </form>
        </div>

        {/* Right Side: Visual Heatmap Output */}
        <div className="lg:col-span-2">
          {clusteringResult ? (
            <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl backdrop-blur-md space-y-6">
              <div className="flex justify-between items-center border-b border-slate-800 pb-4">
                <div>
                  <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">{clusteringResult.name}</h3>
                  <p className="text-[10px] text-slate-400 mt-1">Method: {clusteringResult.method} | Metric: {clusteringResult.distance_metric}</p>
                </div>
                <span className="text-xs bg-emerald-500/10 border border-emerald-500/25 px-2.5 py-1 rounded text-emerald-400 font-bold">
                  Calculation Success
                </span>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-4">Distance Heatmap Matrix</h4>
                  <div className="flex justify-center bg-slate-950/45 p-4 rounded-xl border border-slate-800/80">
                    <Plot
                      data={getHeatmapData()}
                      layout={{
                        width: 500,
                        height: 380,
                        margin: { t: 10, b: 35, l: 35, r: 10 },
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#94a3b8', size: 10 }
                      }}
                      config={{ displayModeBar: false }}
                    />
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900/20 border border-slate-800/60 rounded-2xl p-24 text-center text-slate-500 flex flex-col items-center justify-center gap-3 h-full">
              <GitMerge className="w-10 h-10 text-slate-700" />
              <span>Select sequences and run analysis to render the identity distance heatmap.</span>
            </div>
          )}
        </div>

      </div>

    </div>
  );
};
