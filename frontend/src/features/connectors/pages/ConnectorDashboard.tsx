import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../../../services/api';
import { 
  Database, Plus, RefreshCw, Trash2, CheckCircle2, XCircle, 
  HelpCircle, History, ExternalLink, Activity, Info
} from 'lucide-react';

export const ConnectorDashboard = () => {
  const navigate = useNavigate();
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncingId, setSyncingId] = useState<number | null>(null);
  const [testingId, setTestingId] = useState<number | null>(null);
  const [selectedSource, setSelectedSource] = useState<any | null>(null);
  const [syncHistory, setSyncHistory] = useState<any[]>([]);

  const fetchSources = async () => {
    try {
      setLoading(true);
      const data = await apiRequest('/connectors/sources', { service: 'connectors' });
      setSources(data);
      if (data.length > 0 && !selectedSource) {
        setSelectedSource(data[0]);
      }
    } catch (err) {
      console.error('Failed to load data sources:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSyncHistory = async (sourceId: number) => {
    try {
      const history = await apiRequest(`/connectors/sources/${sourceId}/sync/history`, { service: 'connectors' });
      setSyncHistory(history);
    } catch (err) {
      console.error('Failed to load sync history:', err);
    }
  };

  useEffect(() => {
    fetchSources();
  }, []);

  useEffect(() => {
    if (selectedSource) {
      fetchSyncHistory(selectedSource.id);
    } else {
      setSyncHistory([]);
    }
  }, [selectedSource]);

  const handleTestConnection = async (id: number) => {
    setTestingId(id);
    try {
      const result = await apiRequest(`/connectors/sources/${id}/test`, {
        method: 'POST',
        service: 'connectors'
      });
      alert(result.message);
    } catch (err: any) {
      alert(`Test Connection Failed: ${err.message}`);
    } finally {
      setTestingId(null);
    }
  };

  const handleSyncSchema = async (id: number) => {
    setSyncingId(id);
    try {
      await apiRequest(`/connectors/sources/${id}/sync`, {
        method: 'POST',
        service: 'connectors'
      });
      await fetchSources();
      if (selectedSource?.id === id) {
        await fetchSyncHistory(id);
      }
    } catch (err: any) {
      alert(`Schema sync failed: ${err.message}`);
    } finally {
      setSyncingId(null);
    }
  };

  const handleDeleteSource = async (id: number) => {
    if (!confirm('Are you sure you want to delete this data source and all its catalog entities?')) return;
    try {
      await apiRequest(`/connectors/sources/${id}`, {
        method: 'DELETE',
        service: 'connectors'
      });
      setSources(sources.filter(s => s.id !== id));
      if (selectedSource?.id === id) {
        setSelectedSource(null);
      }
    } catch (err: any) {
      alert(`Deletion failed: ${err.message}`);
    }
  };

  const getConnectorBadgeColor = (type: string) => {
    switch (type) {
      case 'postgresql': return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'sqlserver': return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'oracle': return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
      case 'snowflake': return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
      case 'file': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'rest_api': return 'bg-pink-500/10 text-pink-400 border-pink-500/20';
      case 'mongodb': return 'bg-green-500/10 text-green-400 border-green-500/20';
      default: return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';
    }
  };

  return (
    <div className="space-y-6 h-full flex flex-col">
      {/* Top Banner */}
      <div className="flex justify-between items-center bg-[#0c1220] border border-[#1e293b] p-6 rounded-2xl">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <Database className="h-6 w-6 text-sky-400" />
            <span>Enterprise Data Connectors</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Establish data streams from your SQL databases, instruments, and enterprise laboratory suites (ELN, LIMS).
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => navigate('/connectors/sync-monitor')}
            className="flex items-center space-x-2 bg-[#1e293b] hover:bg-[#334155] border border-slate-750 text-slate-200 font-semibold text-sm px-4.5 py-2.5 rounded-xl shadow-md transition-all"
          >
            <Activity className="h-4 w-4 text-sky-400" />
            <span>Monitor Health</span>
          </button>
          <button
            onClick={() => navigate('/connectors/new')}
            className="flex items-center space-x-2 bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-600 hover:to-teal-600 text-white font-semibold text-sm px-5 py-2.5 rounded-xl shadow-lg transition-all transform hover:-translate-y-0.5"
          >
            <Plus className="h-4 w-4" />
            <span>Add Connection</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex flex-col justify-center items-center space-y-3">
          <div className="h-10 w-10 rounded-full border-2 border-sky-500 border-t-transparent animate-spin"></div>
          <span className="text-sm text-slate-400">Loading data sources...</span>
        </div>
      ) : sources.length === 0 ? (
        <div className="flex-1 flex flex-col justify-center items-center text-center p-12 border-2 border-dashed border-[#1e293b] rounded-2xl space-y-4 bg-[#0c1220]/20">
          <Info className="h-12 w-12 text-slate-600" />
          <div>
            <h3 className="font-semibold text-lg text-slate-200">No Data Sources Connected</h3>
            <p className="text-sm text-slate-500 max-w-sm mt-1">
              Add SQL Servers, CSV uploads, or REST endpoints to enable virtual querying for researchers.
            </p>
          </div>
          <button
            onClick={() => navigate('/connectors/new')}
            className="bg-[#1e293b] hover:bg-[#334155] border border-slate-700 text-slate-200 px-5 py-2 rounded-xl text-sm font-semibold transition-all"
          >
            Connect First Source
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
          {/* List of Connected Sources */}
          <div className="lg:col-span-2 space-y-4 overflow-y-auto pr-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-2">Connected Platforms</h2>
            
            {sources.map((source) => (
              <div
                key={source.id}
                onClick={() => setSelectedSource(source)}
                className={`p-5 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between ${
                  selectedSource?.id === source.id
                    ? 'bg-[#101b30] border-sky-500/60 shadow-[0_0_20px_rgba(14,165,233,0.1)]'
                    : 'bg-[#0c1220] border-[#1e293b] hover:border-[#334155] hover:bg-[#0f172a]'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2.5">
                      <span className="font-bold text-white text-base">{source.name}</span>
                      <span className={`px-2.5 py-0.5 border rounded-full text-[10px] font-bold uppercase tracking-wider ${getConnectorBadgeColor(source.connector_type)}`}>
                        {source.connector_type}
                      </span>
                    </div>
                    <p className="text-sm text-slate-400">{source.description}</p>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
                    <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest">Active</span>
                  </div>
                </div>

                <div className="flex justify-between items-center mt-6 pt-4 border-t border-[#1e293b]/60">
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleTestConnection(source.id);
                      }}
                      disabled={testingId === source.id}
                      className="text-xs text-sky-400 hover:text-sky-300 font-semibold flex items-center space-x-1"
                    >
                      <Activity className={`h-3.5 w-3.5 ${testingId === source.id ? 'animate-pulse' : ''}`} />
                      <span>{testingId === source.id ? 'Testing...' : 'Test Connection'}</span>
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSyncSchema(source.id);
                      }}
                      disabled={syncingId === source.id}
                      className="text-xs text-teal-400 hover:text-teal-300 font-semibold flex items-center space-x-1"
                    >
                      <RefreshCw className={`h-3.5 w-3.5 ${syncingId === source.id ? 'animate-spin' : ''}`} />
                      <span>{syncingId === source.id ? 'Syncing...' : 'Sync Schema'}</span>
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/connectors/${source.id}/schema`);
                      }}
                      className="text-xs text-slate-300 hover:text-white font-semibold flex items-center space-x-1"
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                      <span>Browse Dataset</span>
                    </button>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteSource(source.id);
                    }}
                    className="text-rose-500 hover:text-rose-400 p-1.5 rounded-lg hover:bg-rose-500/10 transition-all"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Sync History Logs & Details Panel */}
          <div className="bg-[#0c1220] border border-[#1e293b] rounded-2xl p-5 flex flex-col min-h-0 overflow-y-auto">
            {selectedSource ? (
              <div className="space-y-6">
                <div>
                  <h3 className="font-bold text-white text-base">{selectedSource.name}</h3>
                  <span className="text-xs text-slate-500">Registered on {new Date().toLocaleDateString()}</span>
                </div>

                <div className="space-y-4">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                    <History className="h-3.5 w-3.5 text-sky-400" />
                    <span>Sync Activity Logs</span>
                  </h4>

                  {syncHistory.length === 0 ? (
                    <div className="text-center p-6 border border-dashed border-[#1e293b] rounded-xl text-slate-500 text-xs">
                      No synchronization events recorded. Click "Sync Schema" to populate columns and endpoints.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {syncHistory.map((log) => (
                        <div key={log.id} className="p-3 border border-[#1e293b]/70 bg-[#070b13]/40 rounded-xl flex items-start justify-between space-x-2">
                          <div className="space-y-1">
                            <div className="flex items-center space-x-1.5">
                              {log.sync_status === 'SUCCESS' ? (
                                <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                              ) : (
                                <XCircle className="h-4 w-4 text-rose-500 shrink-0" />
                              )}
                              <span className={`text-xs font-bold ${log.sync_status === 'SUCCESS' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {log.sync_status === 'SUCCESS' ? 'Success' : 'Failed'}
                              </span>
                            </div>
                            <p className="text-[10px] text-slate-500">
                              Started: {new Date(log.started_at).toLocaleString()}
                            </p>
                            {log.error_message && (
                              <p className="text-[11px] text-rose-400 font-mono mt-1 border-t border-rose-500/10 pt-1">
                                {log.error_message}
                              </p>
                            )}
                          </div>
                          
                          <span className="text-[10px] bg-slate-800 text-slate-300 font-bold px-2 py-0.5 rounded-full shrink-0">
                            {log.records_synced} fields
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col justify-center items-center text-center text-slate-500 space-y-2">
                <HelpCircle className="h-8 w-8 text-slate-600" />
                <p className="text-sm font-semibold">Select a Data Source</p>
                <p className="text-xs text-slate-600">Click on any registered platform to inspect sync logs.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
