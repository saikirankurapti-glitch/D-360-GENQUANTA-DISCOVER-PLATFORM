import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../../services/api';
import { Binary, Layers, CheckCircle, Settings } from 'lucide-react';

export const AlignmentPage: React.FC = () => {
  const [sequences, setSequences] = useState<any[]>([]);
  const [activeMode, setActiveMode] = useState<'pairwise' | 'msa'>('pairwise');

  // Pairwise state
  const [seqAId, setSeqAId] = useState('');
  const [seqBId, setSeqBId] = useState('');
  const [alignType, setAlignType] = useState('global');
  const [matchScore, setMatchScore] = useState(1.0);
  const [mismatchScore, setMismatchScore] = useState(-1.0);
  const [openGapScore, setOpenGapScore] = useState(-0.5);
  const [extendGapScore, setExtendGapScore] = useState(-0.1);
  const [pairwiseResult, setPairwiseResult] = useState<any>(null);
  
  // MSA state
  const [selectedMsaIds, setSelectedMsaIds] = useState<string[]>([]);
  const [msaResult, setMsaResult] = useState<any>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSequences = async () => {
    try {
      const data = await apiRequest('/sequences', { service: 'bioinformatics' });
      setSequences(data);
      if (data.length >= 2) {
        setSeqAId(data[0].sequence_id);
        setSeqBId(data[1].sequence_id);
      }
    } catch (err) {
      console.error('Failed to load sequences', err);
    }
  };

  useEffect(() => {
    fetchSequences();
  }, []);

  const handlePairwiseAlignment = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    setPairwiseResult(null);

    const payload = {
      seq_a_id: seqAId,
      seq_b_id: seqBId,
      alignment_type: alignType,
      match_score: Number(matchScore),
      mismatch_score: Number(mismatchScore),
      open_gap_score: Number(openGapScore),
      extend_gap_score: Number(extendGapScore)
    };

    try {
      const res = await apiRequest('/alignments/pairwise', {
        service: 'bioinformatics',
        method: 'POST',
        body: JSON.stringify(payload)
      });
      setPairwiseResult(res);
    } catch (err: any) {
      setError(err.message || 'Alignment execution failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMsaAlignment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedMsaIds.length < 2) {
      setError('Select at least 2 sequences to run MSA.');
      return;
    }
    setError(null);
    setIsLoading(true);
    setMsaResult(null);

    try {
      const res = await apiRequest('/alignments/multiple', {
        service: 'bioinformatics',
        method: 'POST',
        body: JSON.stringify({ seq_ids: selectedMsaIds })
      });
      setMsaResult(res);
    } catch (err: any) {
      setError(err.message || 'MSA execution failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMsaSelect = (id: string) => {
    setSelectedMsaIds((prev) => 
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto py-2 text-slate-100">
      
      {/* Header Tabs */}
      <div className="flex gap-2 border-b border-slate-800 pb-px">
        <button
          onClick={() => { setActiveMode('pairwise'); setError(null); }}
          className={`flex items-center gap-2 px-4 py-2.5 border-b-2 text-sm font-semibold transition-all ${activeMode === 'pairwise' ? 'border-blue-500 text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
        >
          <Binary className="w-4 h-4" />
          Pairwise Sequence Alignment
        </button>
        <button
          onClick={() => { setActiveMode('msa'); setError(null); }}
          className={`flex items-center gap-2 px-4 py-2.5 border-b-2 text-sm font-semibold transition-all ${activeMode === 'msa' ? 'border-blue-500 text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
        >
          <Layers className="w-4 h-4" />
          Multiple Sequence Alignment (MSA)
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/25 text-red-300 rounded-xl text-xs">
          {error}
        </div>
      )}

      {activeMode === 'pairwise' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Controls Card */}
          <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-2xl backdrop-blur-md space-y-4">
            <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <Settings className="w-4 h-4 text-blue-400" />
              Alignment Parameters
            </h3>
            
            <form onSubmit={handlePairwiseAlignment} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 font-semibold mb-1 uppercase tracking-wider">Sequence A</label>
                <select
                  value={seqAId}
                  onChange={(e) => setSeqAId(e.target.value)}
                  className="w-full bg-slate-850 border border-slate-700/60 rounded-lg p-2.5 text-slate-100 outline-none focus:border-blue-500"
                >
                  {sequences.map((s) => (
                    <option key={s.sequence_id} value={s.sequence_id}>{s.name} ({s.sequence_type})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1 uppercase tracking-wider">Sequence B</label>
                <select
                  value={seqBId}
                  onChange={(e) => setSeqBId(e.target.value)}
                  className="w-full bg-slate-850 border border-slate-700/60 rounded-lg p-2.5 text-slate-100 outline-none focus:border-blue-500"
                >
                  {sequences.map((s) => (
                    <option key={s.sequence_id} value={s.sequence_id}>{s.name} ({s.sequence_type})</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1 uppercase tracking-wider">Mode</label>
                  <select
                    value={alignType}
                    onChange={(e) => setAlignType(e.target.value)}
                    className="w-full bg-slate-850 border border-slate-700/60 rounded-lg p-2 text-slate-100 outline-none"
                  >
                    <option value="global">Global (Needleman)</option>
                    <option value="local">Local (Smith-Waterman)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 font-semibold mb-1 uppercase tracking-wider">Match Score</label>
                  <input
                    type="number"
                    step="0.1"
                    value={matchScore}
                    onChange={(e) => setMatchScore(Number(e.target.value))}
                    className="w-full bg-slate-850 border border-slate-700/60 rounded-lg p-2 text-slate-100 outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1 uppercase tracking-wider">Mismatch</label>
                  <input
                    type="number"
                    step="0.1"
                    value={mismatchScore}
                    onChange={(e) => setMismatchScore(Number(e.target.value))}
                    className="w-full bg-slate-850 border border-slate-700/60 rounded-lg p-2 text-slate-100 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-semibold mb-1 uppercase tracking-wider">Gap Open</label>
                  <input
                    type="number"
                    step="0.1"
                    value={openGapScore}
                    onChange={(e) => setOpenGapScore(Number(e.target.value))}
                    className="w-full bg-slate-850 border border-slate-700/60 rounded-lg p-2 text-slate-100 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-semibold mb-1 uppercase tracking-wider">Gap Ext</label>
                  <input
                    type="number"
                    step="0.1"
                    value={extendGapScore}
                    onChange={(e) => setExtendGapScore(Number(e.target.value))}
                    className="w-full bg-slate-850 border border-slate-700/60 rounded-lg p-2 text-slate-100 outline-none"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading || sequences.length < 2 || seqAId === seqBId}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed font-bold rounded-xl transition-all shadow-lg"
              >
                {isLoading ? 'Aligning...' : 'Calculate Alignment'}
              </button>
            </form>
          </div>

          {/* Right Output Card */}
          <div className="lg:col-span-2">
            {pairwiseResult ? (
              <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl backdrop-blur-md space-y-6">
                <div className="flex justify-between items-center border-b border-slate-800 pb-4">
                  <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Alignment Output</h3>
                  <span className="text-xs bg-emerald-500/10 border border-emerald-500/25 px-2.5 py-1 rounded text-emerald-400 font-bold">
                    Score: {pairwiseResult.score}
                  </span>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Alignment String View</h4>
                    <div className="w-full bg-slate-950 border border-slate-800/80 rounded-xl p-4 font-mono text-xs text-blue-300 break-all select-all leading-relaxed shadow-inner">
                      {pairwiseResult.aligned_a}
                      <br />
                      {pairwiseResult.aligned_b}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">ASCII Visualization Map</h4>
                    <pre className="w-full bg-slate-950 border border-slate-800/80 rounded-xl p-4 font-mono text-[10px] text-slate-300 overflow-x-auto whitespace-pre leading-relaxed shadow-inner">
                      {pairwiseResult.visualization}
                    </pre>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/20 border border-slate-800/60 rounded-2xl p-24 text-center text-slate-500 flex flex-col items-center justify-center gap-3 h-full">
                <Binary className="w-10 h-10 text-slate-700" />
                <span>Choose parameters and compute pairwise alignment.</span>
              </div>
            )}
          </div>
        </div>
      ) : (
        // MSA Mode
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Checkbox selector list */}
          <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-2xl backdrop-blur-md space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Select Sequences for MSA</h3>
            
            <form onSubmit={handleMsaAlignment} className="space-y-4 text-xs">
              <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
                {sequences.map((s) => {
                  const checked = selectedMsaIds.includes(s.sequence_id);
                  return (
                    <button
                      type="button"
                      key={s.sequence_id}
                      onClick={() => toggleMsaSelect(s.sequence_id)}
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

              <button
                type="submit"
                disabled={isLoading || selectedMsaIds.length < 2}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed font-bold rounded-xl transition-all shadow-lg"
              >
                {isLoading ? 'Running MSA...' : `Align ${selectedMsaIds.length} Sequences`}
              </button>
            </form>
          </div>

          {/* Clustal output details */}
          <div className="lg:col-span-2">
            {msaResult ? (
              <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl backdrop-blur-md space-y-6">
                <div className="flex justify-between items-center border-b border-slate-800 pb-4">
                  <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">CLUSTAL W Format Output</h3>
                  <span className="text-xs bg-emerald-500/10 border border-emerald-500/25 px-2 py-0.5 rounded text-emerald-400 font-bold">
                    Success
                  </span>
                </div>

                <div className="space-y-4">
                  <div>
                    <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Multiple Sequence Alignment Grid</h4>
                    <pre className="w-full bg-slate-950 border border-slate-800/80 rounded-xl p-4 font-mono text-[11px] text-emerald-300 overflow-x-auto whitespace-pre leading-relaxed shadow-inner">
                      {msaResult.clustal}
                    </pre>
                  </div>
                  <div>
                    <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Calculated Consensus String</h4>
                    <div className="w-full bg-slate-950 border border-slate-800/80 rounded-xl p-4 font-mono text-xs text-blue-300 break-all select-all leading-relaxed shadow-inner">
                      {msaResult.consensus}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/20 border border-slate-800/60 rounded-2xl p-24 text-center text-slate-500 flex flex-col items-center justify-center gap-3 h-full">
                <Layers className="w-10 h-10 text-slate-700" />
                <span>Select at least 2 sequences and execute multiple alignment.</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
