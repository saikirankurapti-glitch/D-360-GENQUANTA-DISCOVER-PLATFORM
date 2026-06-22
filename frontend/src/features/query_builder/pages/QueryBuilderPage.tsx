import { useEffect, useState } from 'react';
import { useQueryBuilderStore } from '../store/useQueryBuilderStore';
import { QueryCanvas } from '../components/QueryCanvas';
import { ConfigPanel } from '../components/ConfigPanel';
import { SQLPreview } from '../components/SQLPreview';
import { 
  Plus, 
  Save, 
  RotateCcw, 
  FolderOpen, 
  Layers, 
  FlaskConical, 
  Microscope, 
  Table, 
  Clock, 
  Database, 
  Zap, 
  X,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

export const QueryBuilderPage = () => {
  const {
    addEntityNode,
    clearCanvas,
    templates,
    fetchTemplates,
    saveTemplate,
    duplicateTemplate,
    loadTemplate,
    compiledSQL,
    validationErrors,
    metadataEntities,
    fetchMetadataEntities
  } = useQueryBuilderStore();

  const [templateName, setTemplateName] = useState('');
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>('');
  const [queryResults, setQueryResults] = useState<{ columns: string[]; rows: any[]; statistics?: any } | null>(null);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  // Pagination & Execution state
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(5); // Show 5 rows per page for premium feel in demo datasets
  const [activeQueryId, setActiveQueryId] = useState<string | null>(null);
  const [explainPlan, setExplainPlan] = useState<string | null>(null);

  useEffect(() => {
    fetchTemplates();
    fetchMetadataEntities();
  }, []);

  const handleSave = async () => {
    if (!templateName.trim()) {
      alert('Please enter a template name.');
      return;
    }
    try {
      setSaveStatus('Saving...');
      await saveTemplate(templateName, 'Saved via visual canvas');
      setSaveStatus('Saved!');
      setTemplateName('');
      setTimeout(() => setSaveStatus(null), 2000);
    } catch (err) {
      setSaveStatus('Save Failed');
    }
  };

  const handleLoadTemplateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const idStr = e.target.value;
    setSelectedTemplateId(idStr);
    if (!idStr) return;

    const selected = templates.find((t) => t.id === Number(idStr));
    if (selected) {
      loadTemplate(selected);
      setTemplateName(selected.name);
    }
  };

  const handleDuplicate = async () => {
    if (!selectedTemplateId) {
      alert('Please select a template to duplicate.');
      return;
    }
    await duplicateTemplate(Number(selectedTemplateId));
    setSelectedTemplateId('');
  };

  // Real Federated Query handlers
  const executeActiveQuery = async (targetPage: number, targetPageSize: number) => {
    if (!compiledSQL || validationErrors.length > 0) return;
    setResultsLoading(true);
    const qId = crypto.randomUUID();
    setActiveQueryId(qId);

    try {
      const response = await fetch('http://localhost:8003/api/v1/query/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('discover_token') || ''}`
        },
        body: JSON.stringify({
          sql: compiledSQL,
          page: targetPage,
          page_size: targetPageSize,
          query_id: qId
        })
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.detail || 'Query execution failed');
      }

      const data = await response.json();
      setQueryResults(data);
      setPage(targetPage);
    } catch (err: any) {
      console.error('Failed to run federated query:', err);
      throw err;
    } finally {
      setResultsLoading(false);
      setActiveQueryId(null);
    }
  };

  const cancelActiveQuery = async () => {
    if (!activeQueryId) return;
    try {
      const response = await fetch(`http://localhost:8003/api/v1/query/cancel/${activeQueryId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('discover_token') || ''}`
        }
      });
      if (response.ok) {
        setActiveQueryId(null);
        setResultsLoading(false);
      }
    } catch (err) {
      console.error('Failed to cancel query:', err);
    }
  };

  const getExplainPlan = async () => {
    if (!compiledSQL || validationErrors.length > 0) return;
    try {
      const response = await fetch('http://localhost:8003/api/v1/query/explain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('discover_token') || ''}`
        },
        body: JSON.stringify({ sql: compiledSQL })
      });
      if (response.ok) {
        const data = await response.json();
        setExplainPlan(data.plan);
      } else {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.detail || 'Explain plan failed');
      }
    } catch (err: any) {
      console.error('Failed to explain query:', err);
      throw err;
    }
  };

  const totalRows = queryResults?.statistics?.total_rows || 0;
  const totalPages = Math.ceil(totalRows / pageSize);

  return (
    <div className="space-y-6 flex-1 flex flex-col select-none">
      {/* Top Template Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-[#0c1220] border border-[#1e293b] p-4 rounded-2xl flex-shrink-0">
        <div className="flex items-center space-x-3">
          <FolderOpen className="h-5 w-5 text-sky-400" />
          <select
            value={selectedTemplateId}
            onChange={handleLoadTemplateChange}
            className="bg-[#070b13] border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-xl focus:border-sky-500 focus:outline-none w-52"
          >
            <option value="">-- Load Saved Template --</option>
            {templates.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
          {selectedTemplateId && (
            <button
              onClick={handleDuplicate}
              className="border border-slate-850 hover:border-slate-800 bg-[#0d1322] hover:bg-[#131b2e] px-3.5 py-2 rounded-xl text-[10px] font-bold text-slate-300 transition-colors cursor-pointer"
            >
              Duplicate
            </button>
          )}
        </div>

        {/* Save/Clear operations */}
        <div className="flex items-center space-x-3">
          <input
            type="text"
            placeholder="Template name..."
            value={templateName}
            onChange={(e) => setTemplateName(e.target.value)}
            className="bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 w-44"
          />
          <button
            onClick={handleSave}
            className="flex items-center space-x-1.5 bg-sky-500 hover:bg-sky-600 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-[0_4px_15px_rgba(14,165,233,0.3)] transition-colors cursor-pointer"
          >
            <Save className="h-3.5 w-3.5" />
            <span>{saveStatus || 'Save Template'}</span>
          </button>
          <button
            onClick={clearCanvas}
            className="flex items-center space-x-1.5 border border-rose-500/30 hover:border-rose-500 text-rose-400 px-4 py-2 rounded-xl text-xs font-bold hover:bg-rose-500/10 transition-colors cursor-pointer"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Clear Canvas</span>
          </button>
        </div>
      </div>

      {/* Main Workspace grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[480px] flex-shrink-0">
        
        {/* Entity Selector Sidebar */}
        <div className="glass-panel border border-slate-800 rounded-2xl p-5 flex flex-col justify-between space-y-6">
          <div className="space-y-6">
            <div className="flex items-center space-x-2 border-b border-slate-850 pb-3">
              <Layers className="h-5 w-5 text-sky-400" />
              <h4 className="font-bold text-white text-sm">Query Entities</h4>
            </div>

            <div className="space-y-3">
              <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Drag or click to insert</p>
              
              <button
                onClick={() => addEntityNode('Compound')}
                className="w-full flex items-center justify-between p-3.5 bg-[#0d1322] border border-slate-800 hover:border-sky-500/40 rounded-xl transition-all cursor-pointer group text-left"
              >
                <div className="flex items-center space-x-3">
                  <div className="bg-sky-500/10 p-2 rounded-lg text-sky-400 group-hover:bg-sky-500/25">
                    <FlaskConical className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-white">Compounds</p>
                    <p className="text-[9px] text-slate-500 mt-0.5">SMILES, weight, partition...</p>
                  </div>
                </div>
                <Plus className="h-4 w-4 text-slate-600 group-hover:text-sky-400" />
              </button>

              <button
                onClick={() => addEntityNode('Assay')}
                className="w-full flex items-center justify-between p-3.5 bg-[#0d1322] border border-slate-800 hover:border-teal-500/40 rounded-xl transition-all cursor-pointer group text-left"
              >
                <div className="flex items-center space-x-3">
                  <div className="bg-teal-500/10 p-2 rounded-lg text-teal-400 group-hover:bg-teal-500/25">
                    <Microscope className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-white">BioAssays</p>
                    <p className="text-[9px] text-slate-500 mt-0.5">IC50, targets, cell-lines...</p>
                  </div>
                </div>
                <Plus className="h-4 w-4 text-slate-600 group-hover:text-teal-400" />
              </button>

              {/* Dynamic Metadata Entities */}
              {metadataEntities
                .filter(ent => ent.entity_type === 'Table' || ent.entity_type === 'Dataset')
                .map((ent: any) => (
                  <button
                    key={ent.entity_key}
                    onClick={() => addEntityNode(ent.entity_key, ent.name)}
                    className="w-full flex items-center justify-between p-3.5 bg-[#0d1322] border border-slate-800 hover:border-purple-500/40 rounded-xl transition-all cursor-pointer group text-left animate-fade-in"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="bg-purple-500/10 p-2 rounded-lg text-purple-400 group-hover:bg-purple-500/25">
                        <Table className="h-4 w-4" />
                      </div>
                      <div className="max-w-[130px] truncate">
                        <p className="text-xs font-bold text-white truncate">{ent.name}</p>
                        <p className="text-[9px] text-slate-500 mt-0.5 truncate">{ent.entity_key.split('.')[0] || 'Synced Table'}</p>
                      </div>
                    </div>
                    <Plus className="h-4 w-4 text-slate-600 group-hover:text-purple-400" />
                  </button>
                ))}
            </div>
          </div>

          <div className="p-3.5 bg-[#0a0f1b] border border-slate-900 rounded-xl text-[10px] text-slate-500 leading-relaxed">
            <span className="font-bold text-slate-400 block mb-1">DUCKDB FEDERATION</span>
            Attach databases and file directories to execute cross-entity SQL in real-time.
          </div>
        </div>

        {/* React Flow Canvas (Takes 2 cols) */}
        <div className="lg:col-span-2 h-full flex flex-col overflow-hidden">
          <QueryCanvas />
        </div>

        {/* Configurations panel (Takes 1 col) */}
        <div className="h-full flex flex-col overflow-hidden">
          <ConfigPanel />
        </div>
      </div>

      {/* SQL Preview and Output Results grid */}
      <div className="h-64 grid grid-cols-1 md:grid-cols-2 gap-6 flex-shrink-0 min-h-0 select-text">
        <SQLPreview 
          onRunQuery={executeActiveQuery} 
          onExplainPlan={getExplainPlan}
          onCancelQuery={cancelActiveQuery}
          isExecuting={resultsLoading}
          hasActiveQuery={!!activeQueryId}
        />

        {/* Query Results Log */}
        <div className="glass-panel border border-slate-800 rounded-2xl p-5 flex flex-col h-full overflow-hidden shadow-[0_8px_30px_rgba(0,0,0,0.3)]">
          <div className="flex justify-between items-center border-b border-slate-850 pb-3 flex-shrink-0">
            <div className="flex items-center space-x-2">
              <Table className="h-5 w-5 text-teal-400" />
              <h4 className="font-bold text-white text-sm">Query Results Log</h4>
            </div>

            {/* Pagination Size Selector */}
            {queryResults && (
              <div className="flex items-center space-x-1.5">
                <span className="text-[10px] text-slate-500">Rows per page:</span>
                <select
                  value={pageSize}
                  onChange={(e) => {
                    const newSize = Number(e.target.value);
                    setPageSize(newSize);
                    executeActiveQuery(1, newSize);
                  }}
                  className="bg-[#070b13] border border-slate-800 text-[10px] text-slate-300 px-2 py-0.5 rounded focus:outline-none focus:border-sky-500 cursor-pointer"
                >
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                </select>
              </div>
            )}
          </div>

          {/* Premium Execution Statistics Header */}
          {queryResults?.statistics && (
            <div className="flex flex-wrap gap-2.5 py-2.5 border-b border-slate-900/60 items-center flex-shrink-0">
              <div className="flex items-center space-x-1.5 text-[9px] bg-slate-900 border border-slate-800/80 px-2 py-1 rounded font-mono font-medium text-slate-300">
                <Clock className="h-3 w-3 text-sky-400" />
                <span>Duration: {queryResults.statistics.execution_time_ms.toFixed(1)}ms</span>
              </div>

              <div className="flex items-center space-x-1.5 text-[9px] bg-slate-900 border border-slate-800/80 px-2 py-1 rounded font-mono font-medium text-slate-300">
                <Zap className={`h-3 w-3 ${queryResults.statistics.cache_hit ? 'text-emerald-400 animate-pulse' : 'text-amber-400'}`} />
                <span>Cache: {queryResults.statistics.cache_hit ? 'HIT' : 'MISS'}</span>
              </div>

              <div className="flex items-center space-x-1.5 text-[9px] bg-slate-900 border border-slate-800/80 px-2 py-1 rounded font-mono font-medium text-slate-300">
                <Database className="h-3 w-3 text-purple-400" />
                <span>Fetched: {Object.keys(queryResults.statistics.source_fetches || {}).length} sources</span>
              </div>

              {/* Source-specific latency metrics */}
              {Object.entries(queryResults.statistics.source_fetches || {}).map(([src, dur]) => (
                <div key={src} className="text-[8px] bg-sky-950/20 border border-sky-500/10 px-2 py-0.5 rounded font-mono text-sky-400 max-w-[150px] truncate" title={`${src}: ${String(dur)}`}>
                  {src}: {String(dur)}
                </div>
              ))}
            </div>
          )}

          <div className="flex-1 overflow-auto mt-3 min-h-0 text-slate-200">
            {resultsLoading ? (
              <div className="h-full flex flex-col justify-center items-center space-y-2">
                <div className="h-5 w-5 border-2 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-xs text-slate-400">Executing DuckDB query...</span>
              </div>
            ) : queryResults ? (
              <div className="overflow-x-auto w-full">
                <table className="w-full text-left border-collapse min-w-[400px]">
                  <thead>
                    <tr className="border-b border-slate-800">
                      {queryResults.columns.map((col) => (
                        <th key={col} className="pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-500 font-mono">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {queryResults.rows.map((row, i) => (
                      <tr key={i} className="border-b border-slate-900/60 hover:bg-slate-900/20 text-xs">
                        {queryResults.columns.map((col) => (
                          <td key={col} className="py-2.5 pr-2 font-medium">
                            {col === 'smiles' ? (
                              <span className="font-mono text-[10px] text-slate-400 bg-slate-950 px-1.5 py-0.5 rounded truncate block max-w-[150px]" title={row[col]}>
                                {row[col]}
                              </span>
                            ) : col === 'entity_key' ? (
                              <span className="font-mono font-bold text-sky-400">{row[col]}</span>
                            ) : typeof row[col] === 'object' && row[col] !== null ? (
                              <span className="font-mono text-teal-400 bg-teal-950/20 px-1.5 py-0.5 rounded border border-teal-500/10 text-[10px]" title={JSON.stringify(row[col])}>
                                {JSON.stringify(row[col])}
                              </span>
                            ) : (
                              String(row[col] ?? '')
                            )}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="h-full flex justify-center items-center text-slate-500 text-xs italic">
                Click "Run Query" in the SQL Preview to execute and view dataset records here
              </div>
            )}
          </div>

          {/* Pagination Footer */}
          {queryResults && totalPages > 1 && (
            <div className="flex justify-between items-center border-t border-slate-850 pt-3 mt-2 flex-shrink-0">
              <span className="text-[10px] text-slate-500 font-mono">
                Showing {(page - 1) * pageSize + 1} - {Math.min(page * pageSize, totalRows)} of {totalRows} records
              </span>
              <div className="flex items-center space-x-1.5">
                <button
                  disabled={page <= 1}
                  onClick={() => executeActiveQuery(page - 1, pageSize)}
                  className="bg-[#0c1220] hover:bg-[#131b2e] disabled:opacity-40 border border-slate-800 text-[10px] text-slate-300 font-bold p-1.5 rounded-lg transition-colors cursor-pointer"
                >
                  <ChevronLeft className="h-3.5 w-3.5" />
                </button>
                <span className="text-[10px] font-mono text-slate-400 px-1">
                  Page {page} of {totalPages}
                </span>
                <button
                  disabled={page >= totalPages}
                  onClick={() => executeActiveQuery(page + 1, pageSize)}
                  className="bg-[#0c1220] hover:bg-[#131b2e] disabled:opacity-40 border border-slate-800 text-[10px] text-slate-300 font-bold p-1.5 rounded-lg transition-colors cursor-pointer"
                >
                  <ChevronRight className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Explain Plan Modal */}
      {explainPlan && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-[#0b1329] border border-slate-800 rounded-2xl w-full max-w-3xl max-h-[80vh] flex flex-col p-6 space-y-4 shadow-[0_20px_50px_rgba(0,0,0,0.5)]">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3 flex-shrink-0">
              <h3 className="font-bold text-white text-sm">DuckDB Execution Plan Compiler</h3>
              <button
                onClick={() => setExplainPlan(null)}
                className="text-slate-400 hover:text-white transition-colors cursor-pointer"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="flex-1 overflow-auto bg-[#070b13] p-4 rounded-xl font-mono text-[10px] text-emerald-400 whitespace-pre leading-relaxed select-text">
              {explainPlan}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
