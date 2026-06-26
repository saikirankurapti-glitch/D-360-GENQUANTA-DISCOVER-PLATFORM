import { useState, useMemo } from 'react';
import { useCompoundStore } from '../store/useCompoundStore';
import { MoleculeSketcher } from '../components/MoleculeSketcher';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { 
  GitMerge, 
  Plus, 
  Trash, 
  Upload, 
  Table, 
  TrendingUp
} from 'lucide-react';

export const SARDecompositionPage = () => {
  const {
    sarScaffold,
    sarCompoundsInput,
    sarDecomposition,
    sarLoading,
    sarError,
    setSARScaffold,
    addSARCompound,
    removeSARCompound,
    setSARCompoundsInput,
    runSARDecomposition,
    clearSAR
  } = useCompoundStore();

  // Manual entry state
  const [newCompoundName, setNewCompoundName] = useState('');
  const [newCompoundSmiles, setNewCompoundSmiles] = useState('');
  const [newCompoundActivity, setNewCompoundActivity] = useState('');

  // Bulk CSV import state
  const [csvText, setCsvText] = useState('');
  const [showBulkImport, setShowBulkImport] = useState(false);

  const handleAddManual = () => {
    if (!newCompoundSmiles.trim() || !newCompoundActivity) {
      alert('SMILES and Activity value are required.');
      return;
    }

    addSARCompound({
      name: newCompoundName.trim() || `Comp-${Date.now().toString().slice(-4)}`,
      smiles: newCompoundSmiles.trim(),
      activity: Number(newCompoundActivity)
    });

    setNewCompoundName('');
    setNewCompoundSmiles('');
    setNewCompoundActivity('');
  };

  const handleBulkImport = () => {
    if (!csvText.trim()) return;

    try {
      const lines = csvText.split('\n');
      const parsed: Array<{ name: string, smiles: string, activity: number }> = [];

      lines.forEach((line, index) => {
        // Skip header or empty line
        if (index === 0 && (line.toLowerCase().includes('smiles') || line.toLowerCase().includes('activity'))) {
          return;
        }
        if (!line.trim()) return;

        const parts = line.split(',');
        if (parts.length >= 2) {
          const name = parts[0]?.trim() || `CSV-${index}`;
          const smiles = parts[1]?.trim();
          const activity = Number(parts[2]?.trim() || 0);

          if (smiles) {
            parsed.push({ name, smiles, activity });
          }
        }
      });

      if (parsed.length > 0) {
        setSARCompoundsInput(parsed);
        setCsvText('');
        setShowBulkImport(false);
      } else {
        alert('Could not find any valid comma-separated rows. Expected format: name,smiles,activity');
      }
    } catch (err) {
      alert('Error parsing CSV input. Please check the structure.');
    }
  };

  // Extract all unique R-group columns present in the response
  const rGroupKeys = useMemo(() => {
    if (!sarDecomposition) return [];
    const keys = new Set<string>();
    sarDecomposition.compounds.forEach((c) => {
      Object.keys(c.r_groups || {}).forEach((k) => keys.add(k));
    });
    return Array.from(keys).sort();
  }, [sarDecomposition]);

  // Dynamically compile columns for AG Grid
  const columnDefs = useMemo<ColDef[]>(() => {
    if (!sarDecomposition) return [];

    const baseCols: ColDef[] = [
      {
        field: 'name',
        headerName: 'Analogue',
        width: 140,
        pinned: 'left',
        cellRenderer: (params: any) => (
          <span className="font-semibold text-slate-100">{params.value}</span>
        )
      },
      {
        field: 'activity',
        headerName: 'Activity (IC50)',
        width: 130,
        cellRenderer: (params: any) => {
          const val = params.value;
          return (
            <span className="font-mono font-bold text-sky-400 bg-sky-500/10 px-2.5 py-1 rounded border border-sky-500/20 text-xs">
              {val} nM
            </span>
          );
        }
      },
      {
        field: 'smiles',
        headerName: 'Full Structure',
        width: 150,
        cellRenderer: (params: any) => {
          if (!params.value) return null;
          const drawUrl = `http://localhost:8004/api/v1/draw?smiles=${encodeURIComponent(params.value)}&size=100`;
          return (
            <div className="h-full flex justify-center items-center py-1 bg-white/5 rounded p-1">
              <img src={drawUrl} alt="compound structure" className="h-full object-contain" />
            </div>
          );
        }
      }
    ];

    // Append dynamic R-groups
    const rGroupCols = rGroupKeys.map((key) => ({
      headerName: key,
      field: `r_groups.${key}`,
      width: 130,
      cellRenderer: (params: any) => {
        const val = params.value;
        if (!val || val === '[H]' || val === 'H') {
          return <span className="text-slate-650 text-xs italic font-medium px-2 block">- [H]</span>;
        }
        const drawUrl = `http://localhost:8004/api/v1/draw?smiles=${encodeURIComponent(val)}&size=80`;
        return (
          <div className="h-full flex justify-center items-center py-1 bg-[#131b2e]/20 rounded p-1 my-0.5" title={val}>
            <img src={drawUrl} alt={key} className="h-full object-contain" />
          </div>
        );
      }
    }));

    return [...baseCols, ...rGroupCols];
  }, [sarDecomposition, rGroupKeys]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 h-full min-h-0 select-none">
      
      {/* Scaffold Sketcher & Input (Span 1) */}
      <div className="lg:col-span-1 flex flex-col space-y-5 h-full overflow-y-auto pr-1">
        
        {/* Core scaffold designer */}
        <div className="flex-shrink-0 h-[430px]">
          <MoleculeSketcher 
            value={sarScaffold} 
            onChange={setSARScaffold} 
            title="Core Scaffold Scaffold" 
          />
        </div>

        {/* Scaffold raw text indicator */}
        <div className="glass-panel border border-slate-800 rounded-2xl p-5 space-y-4 shadow-md flex-shrink-0">
          <div className="space-y-1">
            <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Scaffold SMILES</label>
            <input
              type="text"
              value={sarScaffold}
              onChange={(e) => setSARScaffold(e.target.value)}
              placeholder="Design structure or paste SMILES..."
              className="w-full bg-[#070b13] border border-slate-800 hover:border-slate-700 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 font-mono select-text"
            />
          </div>

          <button
            onClick={runSARDecomposition}
            disabled={sarLoading || !sarScaffold.trim() || sarCompoundsInput.length === 0}
            className="w-full flex items-center justify-center space-x-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-emerald-700 text-white font-bold py-2 px-4 rounded-xl text-xs shadow-[0_4px_15px_rgba(16,185,129,0.3)] transition-colors cursor-pointer"
          >
            <GitMerge className="h-3.5 w-3.5" />
            <span>{sarLoading ? 'Decomposing R-groups...' : 'Decompose Scaffold'}</span>
          </button>
        </div>
      </div>

      {/* Input Compounds Table & Results (Span 3) */}
      <div className="lg:col-span-3 flex flex-col space-y-6 h-full min-h-0 overflow-y-auto pr-1 select-text">
        {sarError && (
          <div className="bg-rose-500/10 border border-rose-500/20 text-rose-450 p-4 rounded-xl text-xs flex-shrink-0">
            <span>Decomposition failed: {sarError}</span>
          </div>
        )}

        {/* Input listing/management */}
        {!sarDecomposition && (
          <div className="glass-panel border border-slate-800 rounded-2xl p-5 flex flex-col flex-1 min-h-0 shadow-lg space-y-4">
            <div className="flex justify-between items-center border-b border-slate-850 pb-3 flex-shrink-0">
              <h3 className="font-bold text-white text-sm">Target Compounds Analogue Activity ({sarCompoundsInput.length})</h3>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => setShowBulkImport(!showBulkImport)}
                  className="flex items-center space-x-1.5 border border-slate-800 hover:border-slate-700 bg-slate-900 px-3 py-1.5 rounded-lg text-[10px] font-bold text-slate-350 transition-colors cursor-pointer"
                >
                  <Upload className="h-3 w-3" />
                  <span>Bulk Import (CSV)</span>
                </button>
              </div>
            </div>

            {/* Bulk Import Dialog */}
            {showBulkImport && (
              <div className="p-4 bg-[#070b13] border border-slate-850 rounded-xl space-y-3 flex-shrink-0 animate-fadeIn">
                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                  Paste Comma-Separated Values (Row format: name,smiles,activity)
                </p>
                <textarea
                  value={csvText}
                  onChange={(e) => setCsvText(e.target.value)}
                  placeholder="Toluene,Cc1ccccc1,50&#10;Phenol,Oc1ccccc1,1&#10;Chlorobenzene,Clc1ccccc1,55"
                  rows={4}
                  className="w-full bg-slate-950 border border-slate-900 rounded-lg p-3 text-xs text-slate-300 font-mono focus:outline-none focus:border-sky-500"
                />
                <div className="flex space-x-2 justify-end">
                  <button
                    onClick={handleBulkImport}
                    className="bg-sky-500 hover:bg-sky-600 text-white text-[10px] font-bold px-3 py-1.5 rounded-lg cursor-pointer"
                  >
                    Import Entries
                  </button>
                  <button
                    onClick={() => setShowBulkImport(false)}
                    className="border border-slate-800 text-slate-400 text-[10px] font-bold px-3 py-1.5 rounded-lg cursor-pointer"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Manual entry row form */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 bg-[#070b13]/60 p-3 rounded-xl border border-slate-850 flex-shrink-0 items-end">
              <div>
                <label className="text-[9px] text-slate-500 font-bold block mb-1">Name</label>
                <input
                  type="text"
                  placeholder="e.g. Phenol"
                  value={newCompoundName}
                  onChange={(e) => setNewCompoundName(e.target.value)}
                  className="w-full bg-[#070b13] border border-slate-800 text-xs px-2.5 py-1.5 rounded-lg text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>
              <div className="md:col-span-2">
                <label className="text-[9px] text-slate-500 font-bold block mb-1">SMILES Structure</label>
                <input
                  type="text"
                  placeholder="e.g. Oc1ccccc1"
                  value={newCompoundSmiles}
                  onChange={(e) => setNewCompoundSmiles(e.target.value)}
                  className="w-full bg-[#070b13] border border-slate-800 text-xs px-2.5 py-1.5 rounded-lg text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                />
              </div>
              <div className="flex space-x-2">
                <div className="flex-1">
                  <label className="text-[9px] text-slate-500 font-bold block mb-1">Activity (nM)</label>
                  <input
                    type="number"
                    placeholder="1.0"
                    value={newCompoundActivity}
                    onChange={(e) => setNewCompoundActivity(e.target.value)}
                    className="w-full bg-[#070b13] border border-slate-800 text-xs px-2.5 py-1.5 rounded-lg text-slate-200 focus:outline-none focus:border-sky-500"
                  />
                </div>
                <button
                  onClick={handleAddManual}
                  className="bg-sky-500 hover:bg-sky-600 text-white font-bold p-2.5 rounded-lg text-xs cursor-pointer flex justify-center items-center h-[32px] self-end"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* List of current input compounds */}
            <div className="flex-1 overflow-y-auto space-y-2 min-h-0 pr-1">
              {sarCompoundsInput.map((comp, idx) => (
                <div
                  key={idx}
                  className="flex justify-between items-center p-3 bg-[#070b13] border border-slate-900 rounded-xl hover:border-slate-800 transition-all"
                >
                  <div className="flex items-center space-x-4">
                    <span className="text-xs font-bold text-white min-w-[120px]">{comp.name}</span>
                    <span className="font-mono text-[10px] text-slate-500 hidden md:inline">{comp.smiles}</span>
                    {comp.smiles && (
                      <img 
                        src={`http://localhost:8004/api/v1/draw?smiles=${encodeURIComponent(comp.smiles)}&size=60`} 
                        alt={comp.name} 
                        className="h-8 object-contain bg-white/5 p-0.5 rounded border border-white/5"
                      />
                    )}
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="font-mono font-bold text-[10px] bg-sky-950/20 text-sky-400 border border-sky-500/10 px-2 py-0.5 rounded">
                      {comp.activity} nM
                    </span>
                    <button
                      onClick={() => removeSARCompound(idx)}
                      className="text-slate-600 hover:text-rose-400 p-1 cursor-pointer transition-colors"
                    >
                      <Trash className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Decomposition Results matrix */}
        {sarDecomposition && (
          <div className="flex-1 flex flex-col space-y-6 min-h-0 select-text animate-fadeIn">
            {/* The main decomposition matrix layout */}
            <div className="glass-panel border border-slate-800 rounded-2xl flex flex-col h-[380px] overflow-hidden shadow-lg flex-shrink-0">
              <div className="p-4 border-b border-slate-850 flex justify-between items-center bg-[#0c1220]/50 flex-shrink-0">
                <div className="flex items-center space-x-2">
                  <Table className="h-5 w-5 text-emerald-450" />
                  <span className="font-bold text-white text-sm">
                    R-Group Decomposition Matrix ({sarDecomposition.compounds.length} Analogues)
                  </span>
                </div>
                <button
                  onClick={clearSAR}
                  className="text-slate-500 hover:text-slate-350 text-xs font-bold uppercase cursor-pointer"
                >
                  Reset Analysis
                </button>
              </div>

              <div className="flex-1 ag-theme-quartz-dark text-slate-100 min-h-0 relative">
                <AgGridReact
                  rowData={sarDecomposition.compounds}
                  columnDefs={columnDefs}
                  rowHeight={64}
                  defaultColDef={{
                    sortable: true,
                    filter: true,
                    resizable: true,
                  }}
                />
              </div>
            </div>

            {/* Activity cliffs segment */}
            <div className="glass-panel border border-slate-800 rounded-2xl p-5 space-y-3 flex-1 overflow-y-auto shadow-lg max-h-[300px]">
              <div className="flex items-center space-x-2 border-b border-slate-850 pb-2 flex-shrink-0">
                <TrendingUp className="h-4.5 w-4.5 text-teal-400 animate-pulse" />
                <h4 className="font-bold text-white text-sm">Detected Activity Cliffs</h4>
              </div>

              <div className="space-y-2.5">
                {sarDecomposition.activity_cliffs.length === 0 ? (
                  <div className="h-16 flex justify-center items-center text-slate-500 text-xs italic">
                    No significant activity cliffs detected (ratio &gt; 10x with matching R-substitutions).
                  </div>
                ) : (
                  sarDecomposition.activity_cliffs.map((cliff, i) => (
                    <div 
                      key={i}
                      className="p-3 bg-amber-500/5 border border-amber-500/15 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs"
                    >
                      <div className="space-y-1">
                        <p className="font-bold text-slate-200">
                          Cliff between <span className="text-sky-400 font-mono">{cliff.compound_a}</span> and <span className="text-sky-405 font-mono">{cliff.compound_b}</span>
                        </p>
                        <p className="text-[10px] text-slate-500">
                          Substituting R-group <span className="font-mono font-bold text-amber-450">{cliff.differing_r_group}</span>: 
                          <span className="font-mono text-[9px] text-slate-400 bg-slate-900 border border-slate-850 rounded px-1.5 py-0.5 ml-1 select-all">{cliff.group_a}</span> 
                          <span className="mx-1.5 text-slate-650">&rarr;</span> 
                          <span className="font-mono text-[9px] text-slate-400 bg-slate-900 border border-slate-850 rounded px-1.5 py-0.5 select-all">{cliff.group_b}</span>
                        </p>
                      </div>

                      <div className="flex items-center space-x-3.5 self-end md:self-auto">
                        <div className="text-right">
                          <span className="text-[10px] text-slate-500 block">Activity Shift</span>
                          <span className="font-mono text-slate-400 text-[10px]">
                            {cliff.activity_a} nM vs {cliff.activity_b} nM
                          </span>
                        </div>
                        <span className="bg-amber-500/10 text-amber-400 border border-amber-500/25 px-2.5 py-1 rounded-lg text-[10px] font-bold font-mono">
                          {cliff.activity_ratio.toFixed(1)}x shift
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
