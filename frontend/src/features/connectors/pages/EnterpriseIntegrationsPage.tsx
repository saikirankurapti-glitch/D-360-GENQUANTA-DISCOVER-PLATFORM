import React, { useState, useEffect } from 'react';
import { 
  Plug, RefreshCw, CheckCircle, AlertTriangle, Play, Database, History, Info, Plus, Server, Shield
} from 'lucide-react';

interface DataSource {
  id: number;
  name: string;
  connector_type: string;
  is_active: boolean;
}

interface Checkpoint {
  id: number;
  entity_name: string;
  last_sync_timestamp: string;
  cursor_value: string;
  sync_status: string;
}

export const EnterpriseIntegrationsPage = () => {
  const [sources, setSources] = useState<DataSource[]>([]);
  const [selectedSource, setSelectedSource] = useState<number | null>(null);
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Wizard state
  const [showWizard, setShowWizard] = useState(false);
  const [newSource, setNewSource] = useState({
    name: '',
    connector_type: 'eln',
    vendor: 'benchling',
    api_url: 'https://benchling.sandbox.com/api/v1',
    auth_token: '',
    client_id: '',
    client_secret: '',
    use_simulator: true
  });

  // Browser state
  const [browserEntity, setBrowserEntity] = useState('experiments');
  const [browsedRecords, setBrowsedRecords] = useState<any[]>([]);

  useEffect(() => {
    fetchSources();
  }, []);

  useEffect(() => {
    if (selectedSource) {
      fetchCheckpoints(selectedSource);
      fetchBrowsedRecords(selectedSource, browserEntity);
    }
  }, [selectedSource, browserEntity]);

  const fetchSources = async () => {
    try {
      const resp = await fetch('http://localhost:8005/api/v1/connectors/sources');
      if (resp.ok) {
        const data = await resp.json();
        // Filter to only enterprise types
        const enterprise = data.filter((s: any) => ['eln', 'lims', 'assay'].includes(s.connector_type));
        setSources(enterprise);
        if (enterprise.length > 0 && !selectedSource) {
          setSelectedSource(enterprise[0].id);
        }
      }
    } catch (err) {
      console.error('Error fetching data sources:', err);
    }
  };

  const fetchCheckpoints = async (sourceId: number) => {
    try {
      const resp = await fetch(`http://localhost:8005/api/v1/connectors/sources/${sourceId}/sync-checkpoints`);
      if (resp.ok) {
        setCheckpoints(await resp.json());
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchBrowsedRecords = async (sourceId: number, entity: string) => {
    try {
      // Direct query from connector
      const fieldsResp = await fetch(`http://localhost:8005/api/v1/connectors/sources/${sourceId}/entities`);
      if (!fieldsResp.ok) return;
      const entities = await fieldsResp.json();
      const entityData = entities.find((e: any) => e.physical_name.toLowerCase() === entity.toLowerCase());
      if (!entityData) return;
      
      const fields = entityData.fields.map((f: any) => f.physical_name);
      
      const resp = await fetch(`http://localhost:8005/api/v1/connectors/sources/${sourceId}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entity, fields, limit: 10 })
      });
      if (resp.ok) {
        const queryRes = await resp.json();
        const records = queryRes.rows.map((row: any) => {
          const obj: any = {};
          queryRes.columns.forEach((col: string, idx: number) => {
            obj[col] = row[idx];
          });
          return obj;
        });
        setBrowsedRecords(records);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateSource = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const creds: any = {
        api_url: newSource.api_url,
        use_simulator: newSource.use_simulator
      };
      if (newSource.auth_token) {
        creds.auth_token = newSource.auth_token;
      } else {
        creds.client_id = newSource.client_id;
        creds.client_secret = newSource.client_secret;
      }

      // 1. Create Source and config
      const resp = await fetch('http://localhost:8005/api/v1/connectors/sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newSource.name,
          connector_type: newSource.connector_type,
          credentials: creds,
          additional_params: { vendor: newSource.vendor }
        })
      });

      if (resp.ok) {
        const sourceData = await resp.json();
        
        // 2. Trigger initial schema sync
        await fetch(`http://localhost:8005/api/v1/connectors/sources/${sourceData.id}/sync`, { method: 'POST' });
        fetchSources();
        setSelectedSource(sourceData.id);
        setShowWizard(false);
      } else {
        const errorText = await resp.text();
        console.error('Failed to create source:', errorText);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const triggerFullSync = async (sourceId: number) => {
    setIsLoading(true);
    try {
      const resp = await fetch(`http://localhost:8005/api/v1/connectors/sources/${sourceId}/sync`, {
        method: 'POST'
      });
      if (resp.ok) {
        fetchCheckpoints(sourceId);
        fetchBrowsedRecords(sourceId, browserEntity);
        alert('Full Metadata Schema Synchronization successfully completed!');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const triggerIncrementalSync = async (sourceId: number, entity: string) => {
    setIsLoading(true);
    try {
      const resp = await fetch(`http://localhost:8005/api/v1/connectors/sources/${sourceId}/sync-incremental/${entity}`, {
        method: 'POST'
      });
      if (resp.ok) {
        const resData = await resp.json();
        fetchCheckpoints(sourceId);
        fetchBrowsedRecords(sourceId, browserEntity);
        alert(`Incremental CDC Sync Successful!\nCreated: ${resData.created}\nUpdated: ${resData.updated}\nDeleted: ${resData.deleted}`);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8 flex-1 flex flex-col">
      {/* Upper overview header dashboard */}
      <div className="flex justify-between items-center">
        <div>
          <p className="text-slate-400 text-sm">Enterprise lab integrations for Certara/D360 parity.</p>
        </div>
        <button
          onClick={() => setShowWizard(true)}
          className="flex items-center space-x-2 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-[0_0_20px_rgba(14,165,233,0.2)] border border-sky-400/20"
        >
          <Plus className="h-4 w-4" />
          <span>Integrate Vendor</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 flex-1">
        {/* Connection side-pane list */}
        <div className="bg-[#0c1220] border border-[#1e293b] rounded-xl p-5 space-y-4 flex flex-col">
          <h3 className="font-semibold text-slate-300 text-sm tracking-wider uppercase flex items-center space-x-2">
            <Server className="h-4 w-4 text-sky-400" />
            <span>Active Integrations</span>
          </h3>
          <div className="space-y-2 flex-1 overflow-y-auto">
            {sources.length === 0 ? (
              <p className="text-slate-500 text-xs py-4 text-center">No enterprise integrations active.</p>
            ) : (
              sources.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setSelectedSource(s.id)}
                  className={`w-full text-left p-3 rounded-lg border text-sm font-medium transition-all ${
                    selectedSource === s.id
                      ? 'bg-sky-500/10 border-sky-500/50 text-sky-400 shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)]'
                      : 'bg-[#0f172a]/40 border-[#1e293b] text-slate-400 hover:bg-[#0f172a]'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-slate-200">{s.name}</span>
                    <span className="text-[10px] uppercase font-bold tracking-widest bg-sky-500/10 px-2 py-0.5 rounded text-sky-400">
                      {s.connector_type}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 mt-2 text-xs text-slate-500">
                    <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
                    <span>Synchronized</span>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Integration details pane */}
        <div className="lg:grid-cols-3 lg:col-span-3 space-y-8">
          {selectedSource ? (
            <>
              {/* Sync Dashboard Controls */}
              <div className="bg-[#0c1220] border border-[#1e293b] rounded-xl p-6 space-y-6">
                <div className="flex justify-between items-center border-b border-[#1e293b] pb-4">
                  <div>
                    <h2 className="text-lg font-bold text-white flex items-center space-x-2">
                      <Plug className="h-5 w-5 text-sky-400" />
                      <span>{sources.find(s => s.id === selectedSource)?.name} Details</span>
                    </h2>
                    <p className="text-slate-400 text-xs mt-1">Status: Active & Online</p>
                  </div>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => triggerFullSync(selectedSource)}
                      disabled={isLoading}
                      className="flex items-center space-x-2 bg-[#1e293b] hover:bg-[#334155] border border-[#334155] text-slate-200 px-4 py-2 rounded-lg text-xs font-semibold transition-all"
                    >
                      <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                      <span>Sync Schema</span>
                    </button>
                    <button
                      onClick={() => triggerIncrementalSync(selectedSource, browserEntity)}
                      disabled={isLoading}
                      className="flex items-center space-x-2 bg-sky-500 hover:bg-sky-400 text-white px-4 py-2 rounded-lg text-xs font-semibold transition-all shadow-[0_0_15px_rgba(14,165,233,0.1)]"
                    >
                      <Play className="h-4 w-4" />
                      <span>Run Incremental Sync</span>
                    </button>
                  </div>
                </div>

                {/* CDC sync checkpoints */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-slate-300 text-xs tracking-wider uppercase flex items-center space-x-2">
                    <History className="h-4 w-4 text-sky-400" />
                    <span>Change Data Capture (CDC) Checkpoints</span>
                  </h3>
                  <div className="overflow-x-auto border border-[#1e293b] rounded-lg">
                    <table className="min-w-full divide-y divide-[#1e293b] text-left text-xs">
                      <thead className="bg-[#0f172a]">
                        <tr className="text-slate-400 font-bold uppercase tracking-wider">
                          <th className="px-6 py-3">Entity Name</th>
                          <th className="px-6 py-3">Last Sync Date</th>
                          <th className="px-6 py-3">Delta Cursor Value</th>
                          <th className="px-6 py-3">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#1e293b] text-slate-300">
                        {checkpoints.length === 0 ? (
                          <tr>
                            <td colSpan={4} className="px-6 py-4 text-center text-slate-500">No delta check points recorded. Run sync to initialize.</td>
                          </tr>
                        ) : (
                          checkpoints.map((c) => (
                            <tr key={c.id} className="hover:bg-[#131b2e]/30">
                              <td className="px-6 py-3 font-semibold text-white">{c.entity_name}</td>
                              <td className="px-6 py-3">{new Date(c.last_sync_timestamp).toLocaleString()}</td>
                              <td className="px-6 py-3 font-mono text-sky-400">{c.cursor_value || 'None'}</td>
                              <td className="px-6 py-3">
                                <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                                  c.sync_status === 'SUCCESS' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                                }`}>
                                  {c.sync_status === 'SUCCESS' ? <CheckCircle className="h-3 w-3" /> : <AlertTriangle className="h-3 w-3" />}
                                  <span>{c.sync_status}</span>
                                </span>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              {/* Dynamic Virtual Data Browser */}
              <div className="bg-[#0c1220] border border-[#1e293b] rounded-xl p-6 space-y-6">
                <div className="flex justify-between items-center border-b border-[#1e293b] pb-4">
                  <h3 className="font-semibold text-slate-300 text-xs tracking-wider uppercase flex items-center space-x-2">
                    <Database className="h-4 w-4 text-sky-400" />
                    <span>Virtual Entity Data Browser</span>
                  </h3>
                  <div className="flex space-x-2 bg-[#0f172a] p-1 rounded-lg border border-[#1e293b]">
                    {['experiments', 'projects', 'protocols', 'samples', 'tests', 'assays', 'results', 'plates'].map((e) => (
                      <button
                        key={e}
                        onClick={() => setBrowserEntity(e)}
                        className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
                          browserEntity === e
                            ? 'bg-sky-500 text-white shadow'
                            : 'text-slate-400 hover:text-white'
                        }`}
                      >
                        {e}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="overflow-x-auto border border-[#1e293b] rounded-lg">
                  {browsedRecords.length === 0 ? (
                    <div className="p-8 text-center text-slate-500 text-xs">
                      No virtual records available for this type. Make sure connection is connected and synced.
                    </div>
                  ) : (
                    <table className="min-w-full divide-y divide-[#1e293b] text-left text-xs">
                      <thead className="bg-[#0f172a] text-slate-400">
                        <tr>
                          {Object.keys(browsedRecords[0]).map((k) => (
                            <th key={k} className="px-6 py-3 font-bold uppercase tracking-wider">{k}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#1e293b] text-slate-300">
                        {browsedRecords.map((r, i) => (
                          <tr key={i} className="hover:bg-[#131b2e]/30">
                            {Object.values(r).map((val: any, j) => (
                              <td key={j} className="px-6 py-3 font-medium">{val ? String(val) : '—'}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-[#0c1220] border border-[#1e293b] rounded-xl p-12 text-center text-slate-400 space-y-4">
              <Info className="h-12 w-12 text-slate-600 mx-auto" />
              <p className="text-sm">Please select or register an enterprise integration connection to view settings, CDC sync history, and browse entities.</p>
            </div>
          )}
        </div>
      </div>

      {/* Wizard Modal */}
      {showWizard && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-[#0c1220] border border-[#1e293b] rounded-2xl w-full max-w-xl p-6 space-y-6 shadow-2xl animate-in fade-in zoom-in duration-200">
            <div className="flex justify-between items-center border-b border-[#1e293b] pb-4">
              <h3 className="font-bold text-lg text-white flex items-center space-x-2">
                <Plus className="h-5 w-5 text-sky-400" />
                <span>Integrate Enterprise Scientific System</span>
              </h3>
              <button onClick={() => setShowWizard(false)} className="text-slate-400 hover:text-white">&times;</button>
            </div>
            
            <form onSubmit={handleCreateSource} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-slate-400 font-bold uppercase tracking-wider block">Integration Name</label>
                  <input
                    type="text"
                    required
                    value={newSource.name}
                    onChange={(e) => setNewSource({ ...newSource, name: e.target.value })}
                    className="w-full bg-[#0f172a] border border-[#1e293b] rounded-lg px-3 py-2 text-white outline-none focus:border-sky-500"
                    placeholder="Benchling Production R&D"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-slate-400 font-bold uppercase tracking-wider block">System Type</label>
                  <select
                    value={newSource.connector_type}
                    onChange={(e) => setNewSource({ ...newSource, connector_type: e.target.value })}
                    className="w-full bg-[#0f172a] border border-[#1e293b] rounded-lg px-3 py-2 text-white outline-none focus:border-sky-500"
                  >
                    <option value="eln">ELN (Electronic Lab Notebook)</option>
                    <option value="lims">LIMS (Information Management)</option>
                    <option value="assay">Assay Database / Screen</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-slate-400 font-bold uppercase tracking-wider block">Vendor Provider</label>
                  <select
                    value={newSource.vendor}
                    onChange={(e) => setNewSource({ ...newSource, vendor: e.target.value })}
                    className="w-full bg-[#0f172a] border border-[#1e293b] rounded-lg px-3 py-2 text-white outline-none focus:border-sky-500"
                  >
                    {newSource.connector_type === 'eln' && (
                      <>
                        <option value="benchling">Benchling</option>
                        <option value="dotmatics">Dotmatics</option>
                        <option value="signals">Signals Notebook</option>
                      </>
                    )}
                    {newSource.connector_type === 'lims' && (
                      <>
                        <option value="labware">LabWare</option>
                        <option value="labvantage">LabVantage</option>
                        <option value="starlims">STARLIMS</option>
                      </>
                    )}
                    {newSource.connector_type === 'assay' && (
                      <>
                        <option value="bioassay">CDD BioAssay</option>
                        <option value="screening">ActivityBase Screening</option>
                        <option value="hts">HTS Platforms</option>
                      </>
                    )}
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-slate-400 font-bold uppercase tracking-wider block">API URL Endpoint</label>
                  <input
                    type="text"
                    required
                    value={newSource.api_url}
                    onChange={(e) => setNewSource({ ...newSource, api_url: e.target.value })}
                    className="w-full bg-[#0f172a] border border-[#1e293b] rounded-lg px-3 py-2 text-white outline-none focus:border-sky-500"
                  />
                </div>
              </div>

              <div className="border border-sky-500/10 bg-sky-500/5 p-3 rounded-lg flex items-center justify-between">
                <div>
                  <h4 className="text-[11px] font-bold text-white flex items-center space-x-1">
                    <Shield className="h-3.5 w-3.5 text-sky-400" />
                    <span>Run in Offline Simulator Mode</span>
                  </h4>
                  <p className="text-[10px] text-slate-400 mt-0.5">Mock live vendor requests using standard sandbox simulated payloads.</p>
                </div>
                <input
                  type="checkbox"
                  checked={newSource.use_simulator}
                  onChange={(e) => setNewSource({ ...newSource, use_simulator: e.target.checked })}
                  className="h-4 w-4 rounded text-sky-500 bg-[#0f172a] border-[#1e293b] outline-none"
                />
              </div>

              {!newSource.use_simulator && (
                <div className="space-y-3 p-4 border border-[#1e293b] rounded-lg bg-[#0f172a]/50">
                  <div className="space-y-1">
                    <label className="text-slate-400 font-bold uppercase tracking-wider block">API Key / Auth Token</label>
                    <input
                      type="password"
                      value={newSource.auth_token}
                      onChange={(e) => setNewSource({ ...newSource, auth_token: e.target.value })}
                      className="w-full bg-[#0f172a] border border-[#1e293b] rounded-lg px-3 py-2 text-white outline-none focus:border-sky-500"
                      placeholder="Or leave empty to use OAuth2 client details"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <label className="text-slate-400 font-bold uppercase tracking-wider block">OAuth2 Client ID</label>
                      <input
                        type="text"
                        value={newSource.client_id}
                        onChange={(e) => setNewSource({ ...newSource, client_id: e.target.value })}
                        className="w-full bg-[#0f172a] border border-[#1e293b] rounded-lg px-3 py-2 text-white outline-none focus:border-sky-500"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-slate-400 font-bold uppercase tracking-wider block">OAuth2 Client Secret</label>
                      <input
                        type="password"
                        value={newSource.client_secret}
                        onChange={(e) => setNewSource({ ...newSource, client_secret: e.target.value })}
                        className="w-full bg-[#0f172a] border border-[#1e293b] rounded-lg px-3 py-2 text-white outline-none focus:border-sky-500"
                      />
                    </div>
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-3 border-t border-[#1e293b] pt-4">
                <button
                  type="button"
                  onClick={() => setShowWizard(false)}
                  className="bg-[#1e293b] hover:bg-[#334155] border border-[#334155] text-slate-200 px-4 py-2 rounded-lg font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white px-5 py-2 rounded-lg font-semibold shadow-[0_0_15px_rgba(14,165,233,0.15)]"
                >
                  {isLoading ? 'Connecting...' : 'Establish Integration'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
