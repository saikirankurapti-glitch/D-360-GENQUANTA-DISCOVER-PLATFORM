import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../../services/api';
import _createPlotlyComponent from 'react-plotly.js/factory';
import Plotly from 'plotly.js-dist-min';

const createPlotlyComponent = typeof _createPlotlyComponent === 'function'
  ? _createPlotlyComponent
  : (_createPlotlyComponent as any).default;

const Plot = createPlotlyComponent(Plotly);
import { Upload, FileText } from 'lucide-react';

export const SequenceExplorerPage: React.FC = () => {
  const [sequences, setSequences] = useState<any[]>([]);
  const [selectedSeq, setSelectedSeq] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [fastaInput, setFastaInput] = useState('');
  const [importStatus, setImportStatus] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchSequences = async () => {
    try {
      const data = await apiRequest('/sequences', { service: 'bioinformatics' });
      setSequences(data);
      if (data.length > 0 && !selectedSeq) {
        handleSelectSequence(data[0]);
      }
    } catch (err) {
      console.error('Failed to load sequences', err);
    }
  };

  useEffect(() => {
    fetchSequences();
  }, []);

  const handleSelectSequence = async (seq: any) => {
    setSelectedSeq(seq);
    setMetrics(null);
    try {
      const metricsData = await apiRequest(`/sequences/${seq.sequence_id}/metrics`, { service: 'bioinformatics' });
      setMetrics(metricsData);
    } catch (err) {
      console.error('Failed to load sequence metrics', err);
    }
  };

  const handleFastaImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fastaInput.trim()) return;
    setIsLoading(true);
    setImportStatus(null);

    try {
      const res = await apiRequest('/sequences/import', {
        service: 'bioinformatics',
        method: 'POST',
        body: JSON.stringify({ fasta_data: fastaInput }),
      });
      setImportStatus(`Successfully imported ${res.length} sequence(s)!`);
      setFastaInput('');
      fetchSequences();
      if (res.length > 0) {
        handleSelectSequence(res[0]);
      }
    } catch (err: any) {
      setImportStatus(`Import failed: ${err.message || 'Invalid FASTA format.'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const getAminoAcidPlotData = () => {
    if (!metrics || !metrics.composition) return [];
    const labels = Object.keys(metrics.composition);
    const values = Object.values(metrics.composition);
    return [
      {
        x: labels,
        y: values,
        type: 'bar' as const,
        marker: {
          color: 'rgba(99, 102, 241, 0.6)',
          line: { color: 'rgb(99, 102, 241)', width: 1.5 }
        }
      }
    ];
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-7xl mx-auto py-2 text-slate-100">
      
      {/* Left panel: Input & List */}
      <div className="space-y-6 lg:col-span-1">
        
        {/* FASTA Import Card */}
        <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-2xl backdrop-blur-md space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
            <Upload className="w-4 h-4 text-blue-400" />
            <span>Import FASTA Sequence(s)</span>
          </div>
          <form onSubmit={handleFastaImport} className="space-y-3">
            <textarea
              placeholder=">AccessionID Sequence Name&#10;ATGCTAGCTAGCTAGC..."
              value={fastaInput}
              onChange={(e) => setFastaInput(e.target.value)}
              className="w-full h-32 bg-slate-800/60 border border-slate-700/60 rounded-xl p-3 text-xs font-mono text-slate-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-none"
            />
            {importStatus && (
              <div className={`p-2.5 rounded-lg text-xs border ${importStatus.startsWith('Success') ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
                {importStatus}
              </div>
            )}
            <button
              type="submit"
              disabled={isLoading || !fastaInput.trim()}
              className="w-full py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-xs font-bold rounded-xl transition-all shadow-lg shadow-blue-500/10"
            >
              {isLoading ? 'Processing...' : 'Run FASTA Import'}
            </button>
          </form>
        </div>

        {/* Sequence Catalog Card */}
        <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-2xl backdrop-blur-md space-y-3">
          <h3 className="text-sm font-semibold text-slate-200 flex justify-between items-center">
            <span>Sequence Catalog</span>
            <span className="text-xs bg-slate-800 px-2 py-0.5 rounded text-slate-400">{sequences.length} loaded</span>
          </h3>
          <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
            {sequences.map((s) => {
              const selected = selectedSeq?.sequence_id === s.sequence_id;
              return (
                <button
                  key={s.sequence_id}
                  onClick={() => handleSelectSequence(s)}
                  className={`w-full text-left p-3 rounded-xl border text-xs transition-all flex justify-between items-center ${selected ? 'bg-blue-500/15 border-blue-500/40 text-blue-300' : 'bg-slate-800/30 border-slate-700/40 text-slate-300 hover:bg-slate-800/60'}`}
                >
                  <div className="overflow-hidden mr-2">
                    <div className="font-bold truncate">{s.name}</div>
                    <div className="text-[10px] text-slate-500 font-mono mt-0.5">{s.sequence_id}</div>
                  </div>
                  <span className={`px-2 py-0.5 rounded-[5px] text-[9px] font-bold ${s.sequence_type === 'Protein' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' : 'bg-teal-500/20 text-teal-300 border border-teal-500/30'}`}>
                    {s.sequence_type}
                  </span>
                </button>
              );
            })}
            {sequences.length === 0 && (
              <div className="text-slate-500 text-xs text-center py-6">No biological sequences imported yet.</div>
            )}
          </div>
        </div>

      </div>

      {/* Right panel: Sequence viewer & metrics details */}
      <div className="lg:col-span-2 space-y-6">
        {selectedSeq ? (
          <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl backdrop-blur-md space-y-6">
            
            {/* Header info */}
            <div className="border-b border-slate-800 pb-4 flex justify-between items-start">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400 bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 rounded">
                  {selectedSeq.sequence_type}
                </span>
                <h2 className="text-xl font-bold text-slate-100 mt-2">{selectedSeq.name}</h2>
                {selectedSeq.description && (
                  <p className="text-xs text-slate-400 mt-1">{selectedSeq.description}</p>
                )}
              </div>
              <div className="text-right text-xs text-slate-500">
                <div>Accession: <code className="font-mono text-slate-300">{selectedSeq.sequence_id}</code></div>
                <div className="mt-1">Length: <span className="font-bold text-slate-300">{selectedSeq.sequence_string.length} bp/aa</span></div>
              </div>
            </div>

            {/* Sequence String Viewer */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Sequence Block</h4>
              <div className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-300 break-all select-all max-h-[160px] overflow-y-auto leading-relaxed shadow-inner">
                {selectedSeq.sequence_string}
              </div>
            </div>

            {/* Metrics parameters */}
            {metrics && (
              <div className="space-y-4">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Calculated Parameters</h4>
                
                {selectedSeq.sequence_type === 'Protein' ? (
                  <div className="space-y-6">
                    {/* Protein grid parameters */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      <div className="bg-slate-800/30 border border-slate-700/35 p-4 rounded-xl">
                        <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Molecular Weight</div>
                        <div className="text-lg font-bold text-slate-100 mt-1">{metrics.molecular_weight?.toFixed(2)} Da</div>
                      </div>
                      <div className="bg-slate-800/30 border border-slate-700/35 p-4 rounded-xl">
                        <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Isoelectric Point (pI)</div>
                        <div className="text-lg font-bold text-slate-100 mt-1">{metrics.isoelectric_point?.toFixed(2)}</div>
                      </div>
                      <div className="bg-slate-800/30 border border-slate-700/35 p-4 rounded-xl">
                        <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">GRAVY Index</div>
                        <div className="text-lg font-bold text-slate-100 mt-1">{metrics.gravy?.toFixed(3)}</div>
                      </div>
                    </div>

                    {/* Amino Acid count charts */}
                    {metrics.composition && Object.keys(metrics.composition).length > 0 && (
                      <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
                        <h5 className="text-xs font-semibold text-slate-300 mb-3">Amino Acid Distribution</h5>
                        <div className="flex justify-center">
                          <Plot
                            data={getAminoAcidPlotData()}
                            layout={{
                              width: 600,
                              height: 250,
                              margin: { t: 10, b: 35, l: 35, r: 10 },
                              plot_bgcolor: 'rgba(0,0,0,0)',
                              paper_bgcolor: 'rgba(0,0,0,0)',
                              font: { color: '#94a3b8', size: 10 },
                              xaxis: { gridcolor: '#1e293b' },
                              yaxis: { gridcolor: '#1e293b' }
                            }}
                            config={{ displayModeBar: false }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  // Nucleotide metrics
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="bg-slate-800/30 border border-slate-700/35 p-4 rounded-xl">
                      <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">GC Content</div>
                      <div className="text-lg font-bold text-slate-100 mt-1">{(metrics.gc_content * 100).toFixed(2)}%</div>
                    </div>
                    <div className="bg-slate-800/30 border border-slate-700/35 p-4 rounded-xl">
                      <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">AT/AU Content</div>
                      <div className="text-lg font-bold text-slate-100 mt-1">{((1.0 - metrics.gc_content) * 100).toFixed(2)}%</div>
                    </div>
                  </div>
                )}
              </div>
            )}
            
          </div>
        ) : (
          <div className="bg-slate-900/20 border border-slate-800/60 rounded-2xl p-16 text-center text-slate-500 flex flex-col items-center justify-center gap-3">
            <FileText className="w-10 h-10 text-slate-700" />
            <span>Select or import a sequence to inspect biological parameters.</span>
          </div>
        )}
      </div>

    </div>
  );
};
