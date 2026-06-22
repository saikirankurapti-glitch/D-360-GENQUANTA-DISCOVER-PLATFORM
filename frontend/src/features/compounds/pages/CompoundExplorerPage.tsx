import { useState, useMemo } from 'react';
import { useCompoundStore } from '../store/useCompoundStore';
import { MoleculeSketcher } from '../components/MoleculeSketcher';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { 
  Search, 
  Settings, 
  History, 
  Download, 
  FlaskConical, 
  Compass, 
  ChevronRight
} from 'lucide-react';

export const CompoundExplorerPage = () => {
  const {
    searchSmiles,
    searchType,
    similarityThreshold,
    searchResults,
    selectedSearchResult,
    selectedDescriptors,
    searchHistory,
    loading,
    error,
    setSearchSmiles,
    setSearchType,
    setSimilarityThreshold,
    executeSearch,
    selectResult,
    loadHistoryItem,
    clearHistory,
    clearSearch
  } = useCompoundStore();

  const [gridApi, setGridApi] = useState<any>(null);

  // Synchronize selection changes with store
  const onSelectionChanged = (event: any) => {
    const selectedRows = event.api.getSelectedRows();
    if (selectedRows.length > 0) {
      selectResult(selectedRows[0]);
    } else {
      selectResult(null);
    }
  };

  // Export AG Grid data to CSV
  const handleExportCSV = () => {
    if (gridApi) {
      gridApi.exportDataAsCsv({
        fileName: `compound_search_${Date.now()}.csv`,
      });
    }
  };

  // Define AG Grid columns
  const columnDefs = useMemo<ColDef[]>(() => {
    const cols: ColDef[] = [
      {
        field: 'entity_key',
        headerName: 'Entity Key',
        width: 130,
        pinned: 'left',
        cellRenderer: (params: any) => (
          <span className="font-mono font-bold text-sky-450">{params.value}</span>
        ),
      },
      {
        field: 'name',
        headerName: 'Name',
        width: 170,
        cellRenderer: (params: any) => (
          <span className="font-semibold text-slate-100">{params.value}</span>
        ),
      },
      {
        field: 'smiles',
        headerName: 'Structure',
        width: 180,
        suppressHeaderMenuButton: true,
        sortable: false,
        cellRenderer: (params: any) => {
          if (!params.value) return null;
          // Direct render of the SVG endpoint from chemistry_service (port 8004)
          const src = `http://localhost:8004/api/v1/draw?smiles=${encodeURIComponent(params.value)}&size=120`;
          return (
            <div className="h-full flex justify-center items-center py-1 bg-white/5 rounded-lg border border-white/5 p-1 my-1">
              <img src={src} alt="chemical structure" className="h-full object-contain" />
            </div>
          );
        },
      },
      {
        field: 'smiles',
        headerName: 'SMILES Formula',
        width: 280,
        cellRenderer: (params: any) => (
          <span className="font-mono text-[10px] text-slate-400 select-all tracking-tight" title={params.value}>
            {params.value}
          </span>
        ),
      },
    ];

    if (searchType === 'similarity') {
      cols.push({
        field: 'similarity',
        headerName: 'Tanimoto Sim',
        width: 130,
        sort: 'desc',
        cellRenderer: (params: any) => {
          const val = params.value;
          if (val === undefined || val === null) return '-';
          return (
            <span className="font-mono font-bold text-emerald-450 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/25 text-[10px]">
              {(val * 100).toFixed(1)}%
            </span>
          );
        },
      });
    }

    return cols;
  }, [searchType]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-0 select-none">
      
      {/* Left Control Panel (Span 1) */}
      <div className="lg:col-span-1 flex flex-col space-y-5 h-full overflow-y-auto pr-1">
        
        {/* Molecule drawing / import card */}
        <div className="flex-shrink-0 h-[430px]">
          <MoleculeSketcher value={searchSmiles} onChange={setSearchSmiles} title="Structure Query" />
        </div>

        {/* Search settings card */}
        <div className="glass-panel border border-slate-800 rounded-2xl p-5 space-y-4 shadow-md flex-shrink-0">
          <div className="flex items-center space-x-2 border-b border-slate-850 pb-2.5">
            <Settings className="h-4 w-4 text-sky-400" />
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">Search Parameters</h4>
          </div>

          <div className="space-y-3.5">
            {/* Input SMILES field */}
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">SMILES String</label>
              <input
                type="text"
                value={searchSmiles}
                onChange={(e) => setSearchSmiles(e.target.value)}
                placeholder="Paste SMILES (e.g. C1=CC=CC=C1)..."
                className="w-full bg-[#070b13] border border-slate-800 hover:border-slate-700 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 transition-colors font-mono select-text"
              />
            </div>

            {/* Match Type Selection */}
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Search Mode</label>
              <select
                value={searchType}
                onChange={(e) => setSearchType(e.target.value as any)}
                className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-350 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 cursor-pointer"
              >
                <option value="exact">Exact Structure (=)</option>
                <option value="substructure">Substructure Match (&gt;=)</option>
                <option value="similarity">Tanimoto Similarity (%)</option>
              </select>
            </div>

            {/* Threshold slider */}
            {searchType === 'similarity' && (
              <div className="space-y-1.5 animate-fadeIn">
                <div className="flex justify-between items-center text-[10px]">
                  <span className="text-slate-500 font-bold uppercase tracking-wider">Similarity Threshold</span>
                  <span className="text-sky-400 font-mono font-bold">{Math.round(similarityThreshold * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.05"
                  value={similarityThreshold}
                  onChange={(e) => setSimilarityThreshold(Number(e.target.value))}
                  className="w-full accent-sky-500 cursor-pointer bg-slate-805"
                />
              </div>
            )}

            {/* Search actions */}
            <div className="pt-2 flex space-x-2">
              <button
                onClick={executeSearch}
                disabled={loading || !searchSmiles.trim()}
                className="flex-1 flex items-center justify-center space-x-2 bg-sky-500 hover:bg-sky-600 disabled:bg-sky-700 text-white font-bold py-2 rounded-xl text-xs shadow-[0_4px_15px_rgba(14,165,233,0.3)] transition-colors cursor-pointer"
              >
                <Search className="h-3.5 w-3.5" />
                <span>{loading ? 'Searching...' : 'Search'}</span>
              </button>
              <button
                onClick={clearSearch}
                className="border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 px-3 py-2 rounded-xl text-xs transition-colors cursor-pointer"
              >
                Reset
              </button>
            </div>
          </div>
        </div>

        {/* History log card */}
        {searchHistory.length > 0 && (
          <div className="glass-panel border border-slate-800 rounded-2xl p-5 space-y-3 shadow-md flex-shrink-0">
            <div className="flex justify-between items-center border-b border-slate-850 pb-2 flex-shrink-0">
              <div className="flex items-center space-x-2">
                <History className="h-4 w-4 text-sky-400" />
                <h4 className="text-xs font-bold text-white uppercase tracking-wider">Search History</h4>
              </div>
              <button
                onClick={clearHistory}
                className="text-[9px] text-slate-500 hover:text-rose-400 font-bold uppercase cursor-pointer"
              >
                Clear
              </button>
            </div>

            <div className="max-h-[220px] overflow-y-auto space-y-2 pr-1 select-text">
              {searchHistory.map((item) => (
                <div
                  key={item.id}
                  onClick={() => loadHistoryItem(item)}
                  className="p-2.5 bg-[#070b13] border border-slate-900 hover:border-slate-800 hover:bg-[#0d1322] rounded-xl cursor-pointer transition-all group flex items-start justify-between"
                >
                  <div className="space-y-1 overflow-hidden pr-2">
                    <div className="flex items-center space-x-1.5">
                      <span className="text-[9px] bg-slate-850 border border-slate-800/80 text-slate-400 px-1.5 py-0.5 rounded font-mono font-bold uppercase">
                        {item.type}
                      </span>
                      {item.type === 'similarity' && (
                        <span className="text-[9px] text-sky-400 font-mono font-bold">
                          {Math.round(item.threshold * 100)}%
                        </span>
                      )}
                    </div>
                    <p className="font-mono text-[9px] text-slate-500 truncate" title={item.smiles}>
                      {item.smiles}
                    </p>
                  </div>
                  <ChevronRight className="h-3.5 w-3.5 text-slate-600 group-hover:text-sky-400 transition-colors self-center flex-shrink-0" />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Main Table + Details Panel Grid (Span 3) */}
      <div className="lg:col-span-3 flex flex-col space-y-6 h-full min-h-0">
        
        {/* Error panel */}
        {error && (
          <div className="bg-rose-500/10 border border-rose-500/20 text-rose-450 p-4 rounded-xl text-xs flex-shrink-0">
            <span>Chemistry Search Error: {error}</span>
          </div>
        )}

        {/* Results grid panel */}
        <div className="glass-panel border border-slate-800 rounded-2xl overflow-hidden flex flex-col flex-1 min-h-0 shadow-lg">
          <div className="p-4 border-b border-slate-850 flex justify-between items-center bg-[#0c1220]/50 flex-shrink-0">
            <div className="flex items-center space-x-2">
              <FlaskConical className="h-5 w-5 text-teal-400" />
              <span className="font-bold text-white text-sm">
                Chemical Analogue Explorer {searchResults.length > 0 && `(${searchResults.length} matches)`}
              </span>
            </div>
            
            {searchResults.length > 0 && (
              <button
                onClick={handleExportCSV}
                className="flex items-center space-x-1.5 bg-[#131b2e] hover:bg-[#1a253f] border border-slate-800 hover:border-slate-700 text-slate-300 font-bold px-3 py-1.5 rounded-lg text-[10px] transition-colors cursor-pointer"
              >
                <Download className="h-3.5 w-3.5 text-emerald-400" />
                <span>Export CSV</span>
              </button>
            )}
          </div>

          <div className="flex-1 min-h-0 ag-theme-quartz-dark text-slate-100 relative">
            {loading ? (
              <div className="absolute inset-0 z-10 flex flex-col justify-center items-center space-y-3 bg-[#070b13]/40 backdrop-blur-xs">
                <div className="h-7 w-7 border-2 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-xs text-slate-400">Performing structures screening...</span>
              </div>
            ) : searchResults.length === 0 ? (
              <div className="h-full flex flex-col justify-center items-center text-slate-500 space-y-3 p-6 select-text">
                <Compass className="h-12 w-12 text-slate-700 animate-pulse" />
                <p className="text-sm font-bold text-slate-400">Discover Structural Analogues</p>
                <p className="text-xs text-slate-600 text-center max-w-sm leading-relaxed">
                  Draw a structure on the canvas, select your matching threshold, and execute a screen to fetch molecular properties.
                </p>
              </div>
            ) : (
              <AgGridReact
                rowData={searchResults}
                columnDefs={columnDefs}
                rowHeight={64}
                pagination={true}
                paginationPageSize={10}
                paginationPageSizeSelector={[10, 25, 50]}
                rowSelection="single"
                onSelectionChanged={onSelectionChanged}
                onGridReady={(params) => setGridApi(params.api)}
                defaultColDef={{
                  sortable: true,
                  filter: true,
                  resizable: true,
                }}
              />
            )}
          </div>
        </div>

        {/* Selected Compound Descriptors Drawer/Footer (Visible on selection) */}
        {selectedSearchResult && (
          <div className="glass-panel border border-slate-800 rounded-2xl p-5 space-y-4 shadow-xl flex-shrink-0 animate-slideUp select-text">
            <div className="flex justify-between items-start border-b border-slate-850 pb-3">
              <div>
                <h4 className="font-bold text-white text-sm flex items-center space-x-2">
                  <span className="text-sky-450 font-mono">{selectedSearchResult.entity_key}</span>
                  <span className="text-slate-400 font-normal">|</span>
                  <span>{selectedSearchResult.name}</span>
                </h4>
                <p className="text-[10px] text-slate-500 font-mono mt-1 select-all break-all pr-4">
                  {selectedSearchResult.smiles}
                </p>
              </div>
              <button
                onClick={() => setSearchSmiles(selectedSearchResult.smiles)}
                className="text-[10px] border border-slate-800 hover:border-slate-700 bg-slate-900 hover:bg-[#131b2e] px-2.5 py-1.5 rounded-lg text-slate-300 font-bold transition-all cursor-pointer flex-shrink-0"
              >
                Load to Sketcher
              </button>
            </div>

            {/* Chemical Properties Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {/* Formula */}
              <div className="bg-[#070b13] border border-slate-900 rounded-xl p-3 space-y-1">
                <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider block">Formula</span>
                <span className="text-xs font-bold text-white font-mono">
                  {selectedDescriptors ? selectedDescriptors.formula : 'Calculating...'}
                </span>
              </div>

              {/* Molecular Weight */}
              <div className="bg-[#070b13] border border-slate-900 rounded-xl p-3 space-y-1">
                <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider block">Mol Weight</span>
                <span className="text-xs font-bold text-white font-mono">
                  {selectedDescriptors ? selectedDescriptors.mw.toFixed(2) + ' g/mol' : 'Calculating...'}
                </span>
              </div>

              {/* LogP */}
              <div className="bg-[#070b13] border border-slate-900 rounded-xl p-3 space-y-1">
                <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider block">LogP</span>
                <span className="text-xs font-bold text-white font-mono">
                  {selectedDescriptors ? selectedDescriptors.logp.toFixed(3) : 'Calculating...'}
                </span>
              </div>

              {/* TPSA */}
              <div className="bg-[#070b13] border border-slate-900 rounded-xl p-3 space-y-1">
                <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider block">TPSA</span>
                <span className="text-xs font-bold text-white font-mono">
                  {selectedDescriptors ? selectedDescriptors.tpsa.toFixed(1) + ' Å²' : 'Calculating...'}
                </span>
              </div>

              {/* HBD / HBA */}
              <div className="bg-[#070b13] border border-slate-900 rounded-xl p-3 space-y-1">
                <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider block">HBD / HBA</span>
                <span className="text-xs font-bold text-white font-mono">
                  {selectedDescriptors ? `${selectedDescriptors.hbd} / ${selectedDescriptors.hba}` : 'Calculating...'}
                </span>
              </div>

              {/* Rotatable Bonds */}
              <div className="bg-[#070b13] border border-slate-900 rounded-xl p-3 space-y-1">
                <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider block">Rotatable Bonds</span>
                <span className="text-xs font-bold text-white font-mono">
                  {selectedDescriptors ? selectedDescriptors.rotatable_bonds : 'Calculating...'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
