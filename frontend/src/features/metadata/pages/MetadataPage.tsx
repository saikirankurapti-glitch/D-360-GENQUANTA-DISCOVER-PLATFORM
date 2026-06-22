import { useEffect, useState, useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { useMetadataStore } from '../store/useMetadataStore';
import { 
  Database, Search, Filter, ShieldAlert, Sparkles, RefreshCw, 
  Play, ArrowRight, Network, Layers, FileText, CheckCircle2, 
  XCircle, Calendar, Hash, Workflow, GitCommit, Info
} from 'lucide-react';
import type { ColDef } from 'ag-grid-community';
import { ModuleRegistry } from 'ag-grid-community';
import { AllCommunityModule } from 'ag-grid-community';
import { AllEnterpriseModule } from 'ag-grid-enterprise';

ModuleRegistry.registerModules([AllCommunityModule, AllEnterpriseModule]);

export const MetadataPage = () => {
  const {
    entities,
    fields,
    relationships,
    syncHistory,
    versions,
    dataSources,
    loading,
    syncingSourceId,
    fetchMetadata,
    fetchRelationships,
    fetchSyncHistory,
    fetchVersions,
    fetchDataSources,
    syncDatasource
  } = useMetadataStore();

  const [activeTab, setActiveTab] = useState<'catalog' | 'explorer' | 'relationships' | 'history'>('catalog');
  const [searchText, setSearchText] = useState('');
  const [selectedType, setSelectedType] = useState('All');
  
  // Lineage Explorer Selected Entity
  const [selectedExplorerEntityKey, setSelectedExplorerEntityKey] = useState<string>('');
  
  // History Selected Datasource
  const [selectedHistorySourceId, setSelectedHistorySourceId] = useState<number | null>(null);

  const loadAllData = async () => {
    await Promise.all([
      fetchMetadata(),
      fetchRelationships(),
      fetchSyncHistory(),
      fetchDataSources()
    ]);
  };

  useEffect(() => {
    loadAllData();
  }, []);

  // Set default selected explorer entity when entities load
  useEffect(() => {
    if (entities.length > 0 && !selectedExplorerEntityKey) {
      setSelectedExplorerEntityKey(entities[0].entity_key);
    }
  }, [entities, selectedExplorerEntityKey]);

  // Set default history datasource when datasources load
  useEffect(() => {
    if (dataSources.length > 0 && selectedHistorySourceId === null) {
      setSelectedHistorySourceId(dataSources[0].id);
      fetchVersions(dataSources[0].id);
    }
  }, [dataSources, selectedHistorySourceId]);

  // Filter rows based on search text and selected type
  const filteredRowData = useMemo(() => {
    return entities.filter((row) => {
      const matchesType = selectedType === 'All' || 
        (selectedType === 'Compound' && row.entity_type === 'Compound') ||
        (selectedType === 'Assay' && row.entity_type === 'Assay') ||
        (selectedType === 'Table' && row.entity_type === 'Table');
      
      const text = `${row.entity_key} ${row.name} ${row.description || ''} ${JSON.stringify(row.attributes)}`.toLowerCase();
      const matchesSearch = text.includes(searchText.toLowerCase());

      return matchesType && matchesSearch;
    });
  }, [entities, searchText, selectedType]);

  // Construct column definitions dynamically based on available fields
  const columnDefs = useMemo<ColDef[]>(() => {
    const baseCols: ColDef[] = [
      {
        field: 'entity_key',
        headerName: 'Entity Key',
        width: 160,
        pinned: 'left',
        cellRenderer: (params: any) => (
          <span className="font-mono font-bold text-sky-400">{params.value}</span>
        ),
      },
      {
        field: 'entity_type',
        headerName: 'Type',
        width: 120,
        cellRenderer: (params: any) => {
          const val = params.value;
          if (val === 'Compound') {
            return <span className="bg-sky-500/10 text-sky-400 border border-sky-500/20 px-2.5 py-0.5 rounded-full text-[10px] font-bold">Compound</span>;
          } else if (val === 'Assay') {
            return <span className="bg-teal-500/10 text-teal-400 border border-teal-500/20 px-2.5 py-0.5 rounded-full text-[10px] font-bold">Assay</span>;
          } else {
            return <span className="bg-purple-500/10 text-purple-400 border border-purple-500/20 px-2.5 py-0.5 rounded-full text-[10px] font-bold">Table</span>;
          }
        },
      },
      { field: 'name', headerName: 'Name', width: 180 },
      { field: 'description', headerName: 'Description', width: 260, tooltipField: 'description' },
    ];

    // Add dynamic attributes columns from the fields catalog
    const attributeCols = fields.map((f) => ({
      headerName: f.display_name,
      field: `attributes.${f.name}`,
      width: f.name === 'smiles' ? 240 : 130,
      valueGetter: (params: any) => params.data.attributes?.[f.name] || '-',
      cellRenderer: (params: any) => {
        if (f.name === 'smiles') {
          return params.value !== '-' ? (
            <span className="font-mono text-xs text-slate-400 tracking-tight block truncate" title={params.value}>
              {params.value}
            </span>
          ) : (
            <span className="text-slate-600">-</span>
          );
        }
        return <span>{params.value}</span>;
      },
    }));

    return [...baseCols, ...attributeCols];
  }, [fields]);

  // Selected Entity details for explorer tab
  const selectedEntityDetails = useMemo(() => {
    return entities.find(e => e.entity_key === selectedExplorerEntityKey);
  }, [entities, selectedExplorerEntityKey]);

  const handleManualSync = async (sourceId: number) => {
    await syncDatasource(sourceId);
  };

  const selectHistoryDatasource = (sourceId: number) => {
    setSelectedHistorySourceId(sourceId);
    fetchVersions(sourceId);
  };

  return (
    <div className="space-y-6">
      {/* Header and navigation tabs */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <Layers className="h-5 w-5 text-sky-400" />
            <span>Metadata Catalog & Federation</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Explore schema registries, cross-source relations, and versioned metadata lineage.
          </p>
        </div>

        <div className="flex bg-[#070b13] border border-slate-800 p-1 rounded-xl">
          <button
            onClick={() => setActiveTab('catalog')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'catalog'
                ? 'bg-sky-500 text-white shadow-[0_2px_10px_rgba(14,165,233,0.3)]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Catalog Registry
          </button>
          <button
            onClick={() => setActiveTab('explorer')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'explorer'
                ? 'bg-sky-500 text-white shadow-[0_2px_10px_rgba(14,165,233,0.3)]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Schema & Lineage
          </button>
          <button
            onClick={() => setActiveTab('relationships')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'relationships'
                ? 'bg-sky-500 text-white shadow-[0_2px_10px_rgba(14,165,233,0.3)]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Relationship Map
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'history'
                ? 'bg-sky-500 text-white shadow-[0_2px_10px_rgba(14,165,233,0.3)]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Audit & Timeline
          </button>
        </div>
      </div>

      {/* Tab 1: Catalog Registry */}
      {activeTab === 'catalog' && (
        <div className="space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0c1220] border border-[#1e293b] p-4 rounded-2xl">
            <div className="flex flex-1 items-center space-x-3 bg-[#070b13] border border-slate-800 px-3 py-2 rounded-xl focus-within:border-sky-500 transition-all">
              <Search className="h-4 w-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search key, name, properties, or SMILES..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
              />
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-sky-400" />
                <select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="bg-[#070b13] border border-slate-800 text-sm text-slate-300 px-4 py-2 rounded-xl focus:border-sky-500 focus:outline-none"
                >
                  <option value="All">All Types</option>
                  <option value="Compound">Compounds</option>
                  <option value="Assay">Assays</option>
                  <option value="Table">Discovered Tables</option>
                </select>
              </div>

              <button
                onClick={loadAllData}
                disabled={loading}
                className="flex items-center space-x-2 border border-slate-800 hover:border-slate-700 bg-[#0c1220] hover:bg-[#131b2e] px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 transition-all cursor-pointer disabled:opacity-50"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>

          <div className="glass-panel border border-slate-800 rounded-2xl overflow-hidden flex flex-col shadow-[0_8px_30px_rgba(0,0,0,0.4)]">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-[#0c1220]/50">
              <div className="flex items-center space-x-2">
                <Database className="h-5 w-5 text-sky-400" />
                <span className="font-bold text-white text-sm">Entity Registry ({filteredRowData.length} records)</span>
              </div>
              <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider flex items-center space-x-1">
                <Sparkles className="h-3.5 w-3.5 text-teal-400" />
                <span>AG Grid Powered</span>
              </div>
            </div>

            <div className="ag-theme-quartz-dark h-[500px] w-full text-slate-100">
              {loading ? (
                <div className="h-full flex flex-col justify-center items-center space-y-3">
                  <div className="h-8 w-8 rounded-full border-2 border-sky-500 border-t-transparent animate-spin"></div>
                  <span className="text-sm text-slate-400">Loading catalog records...</span>
                </div>
              ) : filteredRowData.length === 0 ? (
                <div className="h-full flex flex-col justify-center items-center text-slate-500 space-y-2">
                  <ShieldAlert className="h-10 w-10 text-slate-600" />
                  <p className="text-sm font-semibold">No records match filters</p>
                  <p className="text-xs text-slate-600">Try adjusting your filters or search terms.</p>
                </div>
              ) : (
                <AgGridReact
                  rowData={filteredRowData}
                  columnDefs={columnDefs}
                  pagination={true}
                  paginationPageSize={15}
                  paginationPageSizeSelector={[10, 15, 30, 50]}
                  defaultColDef={{
                    sortable: true,
                    filter: true,
                    resizable: true,
                  }}
                />
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Schema & Lineage Explorer */}
      {activeTab === 'explorer' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left panel: Entities List */}
          <div className="glass-panel border border-slate-800 rounded-2xl p-5 flex flex-col space-y-4">
            <div className="border-b border-slate-850 pb-3">
              <h3 className="font-bold text-white text-sm flex items-center space-x-2">
                <Layers className="h-4 w-4 text-sky-400" />
                <span>Registered Schema Entities</span>
              </h3>
            </div>
            
            <div className="space-y-2 overflow-y-auto max-h-[550px] pr-1">
              {entities.map((ent) => {
                const isSelected = ent.entity_key === selectedExplorerEntityKey;
                const isTable = ent.entity_type === 'Table';
                const isCompound = ent.entity_type === 'Compound';
                const isAssay = ent.entity_type === 'Assay';
                
                return (
                  <button
                    key={ent.entity_key}
                    onClick={() => setSelectedExplorerEntityKey(ent.entity_key)}
                    className={`w-full flex flex-col items-start p-3 rounded-xl border transition-all text-left cursor-pointer ${
                      isSelected 
                        ? 'bg-sky-500/10 border-sky-500 text-white' 
                        : 'bg-[#070b13] border-slate-850 hover:border-slate-800 text-slate-300'
                    }`}
                  >
                    <div className="flex justify-between items-center w-full">
                      <span className="text-xs font-bold truncate max-w-[170px]">{ent.name}</span>
                      {isCompound && <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-sky-500/10 border border-sky-500/20 text-sky-400 uppercase">Compound</span>}
                      {isAssay && <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-teal-500/10 border border-teal-500/20 text-teal-400 uppercase">Assay</span>}
                      {isTable && <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-purple-500/10 border border-purple-500/20 text-purple-400 uppercase">Table</span>}
                    </div>
                    <span className="text-[9px] font-mono text-slate-500 mt-1 block truncate w-full">{ent.entity_key}</span>
                  </button>
                );
              })}
              {entities.length === 0 && (
                <div className="text-slate-500 text-center py-8 text-xs">No registered entities found.</div>
              )}
            </div>
          </div>

          {/* Right panel: Entity schema & Lineage info */}
          <div className="lg:col-span-2 space-y-6">
            {selectedEntityDetails ? (
              <div className="glass-panel border border-slate-800 rounded-2xl p-6 space-y-6">
                
                {/* Meta details */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-5 gap-3">
                  <div>
                    <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                      <Database className="h-5 w-5 text-purple-400" />
                      <span>{selectedEntityDetails.name}</span>
                    </h3>
                    <p className="text-xs text-slate-400 mt-1">{selectedEntityDetails.description}</p>
                  </div>
                  <div className="bg-[#070b13] border border-slate-850 p-2.5 rounded-xl text-right">
                    <span className="text-[10px] text-slate-500 block">Lineage / Resource Key</span>
                    <span className="font-mono text-xs text-sky-400 font-bold">{selectedEntityDetails.entity_key}</span>
                  </div>
                </div>

                {/* Data lineage visual */}
                <div className="bg-[#070b13] border border-slate-850 p-4 rounded-xl space-y-3">
                  <span className="text-[10px] text-slate-400 font-bold block uppercase tracking-wider">Lineage Origin</span>
                  <div className="flex items-center space-x-3 text-xs">
                    <div className="bg-slate-900 border border-slate-800 p-2 rounded-lg text-slate-300 flex items-center space-x-1.5 font-bold">
                      <Workflow className="h-3.5 w-3.5 text-sky-400" />
                      <span>{selectedEntityDetails.entity_key.split('.')[0] || 'Metadata Service'}</span>
                    </div>
                    <ArrowRight className="h-4 w-4 text-slate-600" />
                    <div className="bg-purple-950/20 border border-purple-800/30 p-2 rounded-lg text-purple-400 flex items-center space-x-1.5 font-bold">
                      <Database className="h-3.5 w-3.5" />
                      <span>{selectedEntityDetails.name}</span>
                    </div>
                  </div>
                </div>

                {/* Column definitions / Attribute table */}
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
                    <FileText className="h-3.5 w-3.5 text-sky-400" />
                    <span>Schema Fields ({selectedEntityDetails.details?.length || 0} fields)</span>
                  </h4>
                  <div className="border border-slate-800 rounded-xl overflow-hidden bg-[#070b13]">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="bg-slate-900/50 border-b border-slate-850 text-slate-400 font-bold">
                          <th className="p-3">Field Name</th>
                          <th className="p-3">Data Type</th>
                          <th className="p-3">Logical Category</th>
                          <th className="p-3">Dynamic Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedEntityDetails.details?.map((det) => (
                          <tr key={det.field_name} className="border-b border-slate-900 text-slate-300 hover:bg-[#0c1220]/30 transition-colors">
                            <td className="p-3 font-mono font-bold text-sky-400">{det.display_name}</td>
                            <td className="p-3">
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-900 text-slate-400 border border-slate-800">
                                {det.data_type}
                              </span>
                            </td>
                            <td className="p-3 text-slate-400">{det.category}</td>
                            <td className="p-3 font-mono text-slate-400 truncate max-w-[200px]" title={det.value}>
                              {det.value}
                            </td>
                          </tr>
                        ))}
                        {(!selectedEntityDetails.details || selectedEntityDetails.details.length === 0) && (
                          <tr>
                            <td colSpan={4} className="p-4 text-center text-slate-500">No columns/attributes available for this schema.</td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

              </div>
            ) : (
              <div className="glass-panel border border-slate-800 rounded-2xl p-8 text-center text-slate-500">
                <Database className="h-10 w-10 text-slate-700 mx-auto mb-3" />
                <p className="text-sm font-semibold">No schema entity selected</p>
                <p className="text-xs text-slate-600">Select an entity from the sidebar to inspect its column structures and source lineage.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Relationship Map */}
      {activeTab === 'relationships' && (
        <div className="glass-panel border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="border-b border-slate-800 pb-4 flex justify-between items-center">
            <div>
              <h3 className="font-bold text-white text-sm flex items-center space-x-2">
                <Network className="h-4 w-4 text-sky-400" />
                <span>Dynamic Entity Relationship Graph</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Visualizing keys mapping datasets across connected warehouses.
              </p>
            </div>
            <span className="text-[10px] bg-sky-500/10 text-sky-400 border border-sky-500/20 px-2 py-0.5 rounded uppercase font-bold">
              {relationships.length} active relations
            </span>
          </div>

          <div className="bg-[#070b13] border border-slate-850 p-6 rounded-2xl min-h-[350px] flex flex-col justify-center items-center relative overflow-hidden">
            
            {relationships.length > 0 ? (
              <div className="w-full max-w-4xl space-y-4">
                {relationships.map((rel) => (
                  <div 
                    key={rel.id} 
                    className="flex flex-col md:flex-row items-center justify-between p-4 bg-[#0c1220]/80 border border-slate-800 hover:border-slate-700 rounded-xl gap-4 transition-all"
                  >
                    {/* Source Table */}
                    <div className="flex items-center space-x-3 w-full md:w-1/3">
                      <div className="bg-sky-500/10 p-2.5 rounded-lg text-sky-400 border border-sky-500/25">
                        <Database className="h-4 w-4" />
                      </div>
                      <div className="truncate">
                        <span className="text-slate-500 text-[10px] block">SOURCE ENTITY</span>
                        <span className="font-bold text-xs text-white block truncate">{rel.source_entity_key.split('.')[1] || rel.source_entity_key}</span>
                        <span className="font-mono text-[9px] text-slate-400 block font-bold">{rel.source_field_name}</span>
                      </div>
                    </div>

                    {/* Join Indicator */}
                    <div className="flex flex-col items-center justify-center w-full md:w-1/3 py-2 border-y md:border-y-0 border-slate-850">
                      <span className="text-[9px] bg-slate-900 border border-slate-800 text-sky-400 px-2 py-0.5 rounded font-bold font-mono">
                        {rel.cardinality} JOIN
                      </span>
                      <div className="flex items-center space-x-2 mt-1">
                        <div className="h-[2px] w-12 bg-gradient-to-r from-sky-500 to-purple-500"></div>
                        <ArrowRight className="h-3 w-3 text-purple-400" />
                        <div className="h-[2px] w-12 bg-gradient-to-r from-purple-500 to-teal-500"></div>
                      </div>
                    </div>

                    {/* Target Table */}
                    <div className="flex items-center space-x-3 w-full md:w-1/3 justify-end text-right">
                      <div className="truncate">
                        <span className="text-slate-500 text-[10px] block">TARGET ENTITY</span>
                        <span className="font-bold text-xs text-white block truncate">{rel.target_entity_key.split('.')[1] || rel.target_entity_key}</span>
                        <span className="font-mono text-[9px] text-slate-400 block font-bold">{rel.target_field_name}</span>
                      </div>
                      <div className="bg-teal-500/10 p-2.5 rounded-lg text-teal-400 border border-teal-500/25">
                        <Database className="h-4 w-4" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-slate-500 space-y-2">
                <Network className="h-10 w-10 text-slate-700 mx-auto" />
                <p className="text-sm font-semibold">No dynamic relationships defined</p>
                <p className="text-xs text-slate-650 max-w-sm">
                  Federate relationships by setting up foreign key mappings inside the Connector Service registries to display cross-datasource links.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 4: Audit & Timeline */}
      {activeTab === 'history' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Data Sources and manual triggers */}
          <div className="glass-panel border border-slate-800 rounded-2xl p-5 flex flex-col space-y-4">
            <div className="border-b border-slate-850 pb-3">
              <h3 className="font-bold text-white text-sm flex items-center space-x-2">
                <Workflow className="h-4 w-4 text-sky-400" />
                <span>Connectors Schema Sync</span>
              </h3>
            </div>

            <div className="space-y-3">
              {dataSources.map((ds) => {
                const isSyncing = syncingSourceId === ds.id;
                const isSelected = selectedHistorySourceId === ds.id;
                
                return (
                  <div
                    key={ds.id}
                    onClick={() => selectHistoryDatasource(ds.id)}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between space-y-3 ${
                      isSelected 
                        ? 'bg-sky-500/5 border-sky-500' 
                        : 'bg-[#070b13] border-slate-850 hover:border-slate-800'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="text-xs font-bold text-white block">{ds.name}</span>
                        <span className="text-[10px] text-slate-500 capitalize">{ds.connector_type} DB</span>
                      </div>
                      
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleManualSync(ds.id);
                        }}
                        disabled={isSyncing}
                        className="flex items-center space-x-1 text-[10px] font-bold px-2 py-1 rounded bg-sky-500 hover:bg-sky-650 text-white disabled:opacity-50 transition-colors"
                      >
                        <Play className={`h-2.5 w-2.5 ${isSyncing ? 'animate-spin' : ''}`} />
                        <span>{isSyncing ? 'Syncing...' : 'Sync Now'}</span>
                      </button>
                    </div>
                  </div>
                );
              })}
              {dataSources.length === 0 && (
                <div className="text-center py-6 text-xs text-slate-500">No data sources configured.</div>
              )}
            </div>
          </div>

          {/* Timeline of schema versions and history */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Version Timelines */}
            <div className="glass-panel border border-slate-800 rounded-2xl p-6 space-y-4">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
                <GitCommit className="h-4 w-4 text-purple-400" />
                <span>Schema Version Timeline</span>
              </h4>
              
              <div className="space-y-4 overflow-y-auto max-h-[300px] pr-2">
                {selectedHistorySourceId !== null && versions[selectedHistorySourceId]?.map((ver) => (
                  <div key={ver.id} className="relative pl-6 border-l-2 border-purple-500/30 pb-2 last:pb-0">
                    <div className="absolute -left-[6px] top-1.5 h-2.5 w-2.5 rounded-full bg-purple-500 border-2 border-slate-950"></div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white flex items-center space-x-1">
                        <Hash className="h-3 w-3 text-purple-400" />
                        <span>Version {ver.version}</span>
                      </span>
                      <span className="text-[10px] text-slate-500 flex items-center space-x-1">
                        <Calendar className="h-3 w-3" />
                        <span>{new Date(ver.created_at).toLocaleString()}</span>
                      </span>
                    </div>
                    <div className="mt-1 bg-slate-900 border border-slate-850 p-2.5 rounded-lg text-[10px] text-slate-350 leading-relaxed">
                      <span className="font-bold text-slate-500 block mb-1">DETECTOR DELTA</span>
                      {ver.changes_detected || 'No changes noted in delta.'}
                    </div>
                  </div>
                ))}

                {(selectedHistorySourceId === null || !versions[selectedHistorySourceId] || versions[selectedHistorySourceId].length === 0) && (
                  <div className="text-center py-8 text-xs text-slate-500 flex flex-col items-center justify-center space-y-2">
                    <Info className="h-8 w-8 text-slate-700" />
                    <span>No version logs recorded. Trigger a manual sync to generate schema milestones.</span>
                  </div>
                )}
              </div>
            </div>

            {/* Ingestion audit runs log */}
            <div className="glass-panel border border-slate-800 rounded-2xl p-6 space-y-4">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
                <FileText className="h-4 w-4 text-sky-400" />
                <span>Federation Sync Log (Runs Audit)</span>
              </h4>

              <div className="overflow-x-auto border border-slate-850 rounded-xl bg-[#070b13]">
                <table className="w-full text-left border-collapse text-[10px]">
                  <thead>
                    <tr className="bg-slate-900/50 border-b border-slate-850 text-slate-400 font-bold">
                      <th className="p-3">Data Source</th>
                      <th className="p-3">Status</th>
                      <th className="p-3">Records Synced</th>
                      <th className="p-3">Changes</th>
                      <th className="p-3">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {syncHistory.map((hist) => {
                      const isSuccess = hist.status === 'SUCCESS';
                      return (
                        <tr key={hist.id} className="border-b border-slate-900 text-slate-300 hover:bg-[#0c1220]/20 transition-colors">
                          <td className="p-3 font-bold text-white">{hist.datasource_name}</td>
                          <td className="p-3">
                            <span className={`inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[9px] font-bold border uppercase ${
                              isSuccess 
                                ? 'bg-green-500/10 text-green-400 border-green-500/20' 
                                : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                            }`}>
                              {isSuccess ? <CheckCircle2 className="h-2.5 w-2.5" /> : <XCircle className="h-2.5 w-2.5" />}
                              <span>{hist.status}</span>
                            </span>
                          </td>
                          <td className="p-3 font-mono">{hist.records_synced} schemas</td>
                          <td className="p-3 max-w-[150px] truncate text-slate-400" title={hist.changes_detected || hist.error_message}>
                            {isSuccess ? (hist.changes_detected || 'Clean sync') : hist.error_message}
                          </td>
                          <td className="p-3 text-slate-500">{new Date(hist.completed_at).toLocaleString()}</td>
                        </tr>
                      );
                    })}
                    {syncHistory.length === 0 && (
                      <tr>
                        <td colSpan={5} className="p-4 text-center text-slate-550">No synchronization runs detected.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
