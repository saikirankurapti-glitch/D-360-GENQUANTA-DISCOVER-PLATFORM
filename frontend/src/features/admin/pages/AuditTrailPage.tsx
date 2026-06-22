import { useState, useEffect, useMemo } from 'react';
import { apiRequest } from '../../../services/api';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { 
  ShieldCheck, 
  Search, 
  RotateCcw, 
  CheckCircle2, 
  XCircle, 
  Info, 
  Layers, 
  FileText,
  Activity
} from 'lucide-react';

interface AuditLog {
  id: number;
  timestamp: string;
  user_id: string | null;
  username: string | null;
  action: string;
  service_name: string;
  endpoint: string | null;
  status: string;
  ip_address: string | null;
  details_json: string | null;
  previous_hash: string | null;
  hash: string;
}

interface VerifyResult {
  log_id: number;
  is_valid: boolean;
  calculated_hash: string;
  database_hash: string;
  message: string;
  chain_intact: boolean;
}

export const AuditTrailPage = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedUser, setSelectedUser] = useState('');
  const [selectedService, setSelectedService] = useState('');
  const [selectedAction, setSelectedAction] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');

  // Selected Log Modal
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [verificationResult, setVerificationResult] = useState<VerifyResult | null>(null);
  const [verifying, setVerifying] = useState(false);

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const queryParams = new URLSearchParams();
      if (selectedUser) queryParams.append('user_id', selectedUser);
      if (selectedService) queryParams.append('service_name', selectedService);
      if (selectedAction) queryParams.append('action', selectedAction);
      if (selectedStatus) queryParams.append('status', selectedStatus);

      const data = await apiRequest(`/audit/logs?${queryParams.toString()}`, {
        service: 'audit'
      });
      setLogs(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load audit logs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [selectedUser, selectedService, selectedAction, selectedStatus]);

  const handleVerify = async (logId: number) => {
    setVerifying(true);
    setVerificationResult(null);
    try {
      const result = await apiRequest(`/audit/logs/${logId}/verify`, {
        service: 'audit'
      });
      setVerificationResult(result);
    } catch (err: any) {
      alert(err.message || 'Verification failed.');
    } finally {
      setVerifying(false);
    }
  };

  const resetFilters = () => {
    setSelectedUser('');
    setSelectedService('');
    setSelectedAction('');
    setSelectedStatus('');
  };

  // Compile unique lists for dropdown filters
  const filterOptions = useMemo(() => {
    const users = new Set<string>();
    const services = new Set<string>();
    const actions = new Set<string>();
    const statuses = new Set<string>();

    logs.forEach(log => {
      if (log.user_id) users.add(log.user_id);
      if (log.service_name) services.add(log.service_name);
      if (log.action) actions.add(log.action);
      if (log.status) statuses.add(log.status);
    });

    return {
      users: Array.from(users).sort(),
      services: Array.from(services).sort(),
      actions: Array.from(actions).sort(),
      statuses: Array.from(statuses).sort()
    };
  }, [logs]);

  // Column definitions for AG Grid
  const columnDefs = useMemo<ColDef[]>(() => [
    {
      field: 'timestamp',
      headerName: 'Timestamp',
      width: 190,
      cellRenderer: (params: any) => (
        <span className="font-mono text-xs text-slate-400">
          {new Date(params.value).toLocaleString()}
        </span>
      )
    },
    {
      field: 'username',
      headerName: 'User',
      width: 140,
      cellRenderer: (params: any) => (
        <span className="font-semibold text-slate-200">
          {params.value || params.data.user_id || 'System'}
        </span>
      )
    },
    {
      field: 'action',
      headerName: 'Action',
      width: 150,
      cellRenderer: (params: any) => (
        <span className="font-mono font-bold text-sky-400 bg-sky-500/10 px-2.5 py-1 rounded border border-sky-500/20 text-xs">
          {params.value}
        </span>
      )
    },
    {
      field: 'service_name',
      headerName: 'Service',
      width: 140,
      cellRenderer: (params: any) => (
        <span className="text-slate-300 font-medium">
          {params.value}
        </span>
      )
    },
    {
      field: 'endpoint',
      headerName: 'API Endpoint',
      width: 180,
      cellRenderer: (params: any) => (
        <span className="font-mono text-xs text-slate-500 truncate block" title={params.value || ''}>
          {params.value || '-'}
        </span>
      )
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      cellRenderer: (params: any) => {
        const val = params.value;
        const isSuccess = val === 'SUCCESS';
        return (
          <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
            isSuccess 
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
              : 'bg-rose-500/10 text-rose-450 border-rose-500/20'
          }`}>
            <span className={`h-1.5 w-1.5 rounded-full ${isSuccess ? 'bg-emerald-450' : 'bg-rose-450'}`} />
            <span>{val}</span>
          </span>
        );
      }
    },
    {
      headerName: 'Actions',
      width: 160,
      pinned: 'right',
      cellRenderer: (params: any) => (
        <div className="flex space-x-2 h-full items-center">
          <button
            onClick={() => {
              setSelectedLog(params.data);
              setVerificationResult(null);
            }}
            className="flex items-center space-x-1 bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-350 hover:text-slate-200 px-2 py-1 rounded text-[10px] font-bold cursor-pointer transition-colors"
          >
            <Info className="h-3 w-3" />
            <span>Details</span>
          </button>
          <button
            onClick={() => handleVerify(params.data.id)}
            className="flex items-center space-x-1 bg-sky-500/10 border border-sky-500/20 hover:border-sky-500/40 text-sky-400 hover:text-sky-300 px-2 py-1 rounded text-[10px] font-bold cursor-pointer transition-colors"
          >
            <ShieldCheck className="h-3 w-3" />
            <span>Verify</span>
          </button>
        </div>
      )
    }
  ], []);

  return (
    <div className="flex flex-col space-y-6 flex-1 min-h-0">
      
      {/* Header Panel */}
      <div className="glass-panel border border-slate-800 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-md flex-shrink-0">
        <div className="space-y-1">
          <div className="flex items-center space-x-2 text-sky-450">
            <ShieldCheck className="h-5 w-5" />
            <h3 className="font-bold text-white text-base">FDA 21 CFR Part 11 Audit Trail</h3>
          </div>
          <p className="text-xs text-slate-500 max-w-2xl">
            Immutably chained log entries securing user activities, authentication, queries, and connectors.
            All operations are cryptographically linked using SHA-256 blocks to provide complete data provenance.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          className="flex items-center space-x-2 border border-slate-850 bg-slate-905 hover:bg-slate-900 px-4 py-2 rounded-xl text-xs font-bold text-slate-300 transition-all cursor-pointer flex-shrink-0"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          <span>Refresh Logs</span>
        </button>
      </div>

      {/* Filters Segment */}
      <div className="grid grid-cols-1 sm:grid-cols-4 lg:grid-cols-5 gap-3 bg-[#0c1220]/45 p-4 rounded-xl border border-slate-850 flex-shrink-0">
        <div>
          <label className="text-[9px] text-slate-500 font-bold block mb-1">Filter by User</label>
          <select
            value={selectedUser}
            onChange={(e) => setSelectedUser(e.target.value)}
            className="w-full bg-[#070b13] border border-slate-800 text-xs px-2.5 py-1.5 rounded-lg text-slate-200 focus:outline-none focus:border-sky-500"
          >
            <option value="">All Users</option>
            {filterOptions.users.map(u => <option key={u} value={u}>{u}</option>)}
          </select>
        </div>
        <div>
          <label className="text-[9px] text-slate-500 font-bold block mb-1">Filter by Service</label>
          <select
            value={selectedService}
            onChange={(e) => setSelectedService(e.target.value)}
            className="w-full bg-[#070b13] border border-slate-800 text-xs px-2.5 py-1.5 rounded-lg text-slate-200 focus:outline-none focus:border-sky-500"
          >
            <option value="">All Services</option>
            {filterOptions.services.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div>
          <label className="text-[9px] text-slate-500 font-bold block mb-1">Filter by Action</label>
          <select
            value={selectedAction}
            onChange={(e) => setSelectedAction(e.target.value)}
            className="w-full bg-[#070b13] border border-slate-800 text-xs px-2.5 py-1.5 rounded-lg text-slate-200 focus:outline-none focus:border-sky-500"
          >
            <option value="">All Actions</option>
            {filterOptions.actions.map(a => <option key={a} value={a}>{a}</option>)}
          </select>
        </div>
        <div>
          <label className="text-[9px] text-slate-500 font-bold block mb-1">Filter by Status</label>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="w-full bg-[#070b13] border border-slate-800 text-xs px-2.5 py-1.5 rounded-lg text-slate-200 focus:outline-none focus:border-sky-500"
          >
            <option value="">All Statuses</option>
            {filterOptions.statuses.map(st => <option key={st} value={st}>{st}</option>)}
          </select>
        </div>
        <div className="flex items-end">
          <button
            onClick={resetFilters}
            className="w-full bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 font-semibold py-1.5 px-3 rounded-lg text-xs transition-colors cursor-pointer flex justify-center items-center space-x-1"
          >
            <Search className="h-3 w-3" />
            <span>Reset Filters</span>
          </button>
        </div>
      </div>

      {/* Main Table Grid */}
      <div className="glass-panel border border-slate-800 rounded-2xl flex flex-col flex-1 overflow-hidden shadow-lg min-h-[300px]">
        {error && (
          <div className="bg-rose-500/10 border border-rose-500/20 text-rose-450 p-4 rounded-t-xl text-xs flex-shrink-0">
            <span>{error}</span>
          </div>
        )}
        
        <div className="flex-1 ag-theme-quartz-dark text-slate-100 min-h-0 relative select-text">
          {loading && (
            <div className="absolute inset-0 bg-[#070b13]/60 flex items-center justify-center z-50">
              <div className="flex flex-col items-center space-y-2">
                <Activity className="h-8 w-8 text-sky-400 animate-spin" />
                <span className="text-xs text-slate-400">Loading audit records...</span>
              </div>
            </div>
          )}
          <AgGridReact
            rowData={logs}
            columnDefs={columnDefs}
            rowHeight={52}
            defaultColDef={{
              sortable: true,
              filter: true,
              resizable: true,
            }}
          />
        </div>
      </div>

      {/* Verification overlay toast if verifying outside modal */}
      {verifying && (
        <div className="fixed bottom-6 right-6 bg-slate-950 border border-slate-850 p-4 rounded-xl shadow-[0_4px_25px_rgba(0,0,0,0.5)] z-50 flex items-center space-x-3 select-none">
          <Activity className="h-5 w-5 text-sky-400 animate-spin" />
          <span className="text-xs text-slate-300 font-medium">Running cryptographic verify...</span>
        </div>
      )}

      {verificationResult && !selectedLog && (
        <div className={`fixed bottom-6 right-6 border p-4 rounded-xl shadow-[0_4px_25px_rgba(0,0,0,0.5)] z-50 flex items-center space-x-3 animate-fadeIn ${
          verificationResult.is_valid 
            ? 'bg-emerald-950/90 border-emerald-500/30 text-emerald-450' 
            : 'bg-rose-950/90 border-rose-500/30 text-rose-450'
        }`}>
          {verificationResult.is_valid ? <CheckCircle2 className="h-5 w-5" /> : <XCircle className="h-5 w-5" />}
          <div className="text-xs">
            <p className="font-bold">{verificationResult.is_valid ? 'Integrity Valid' : 'Integrity Failure'}</p>
            <p className="text-[10px] text-slate-400">{verificationResult.message}</p>
          </div>
          <button 
            onClick={() => setVerificationResult(null)}
            className="text-[10px] font-bold border border-current/20 px-2 py-0.5 rounded hover:bg-white/5 cursor-pointer ml-2"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Log Details Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex justify-center items-center z-50 p-4 select-text">
          <div className="bg-[#0c1220] border border-slate-800 rounded-2xl w-full max-w-3xl overflow-hidden shadow-[0_10px_50px_rgba(0,0,0,0.7)] flex flex-col max-h-[85vh]">
            
            {/* Modal Header */}
            <div className="p-5 border-b border-slate-850 flex justify-between items-center bg-[#070b13]/60">
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-sky-400" />
                <span className="font-bold text-white text-sm">Audit Log Record Details (ID: {selectedLog.id})</span>
              </div>
              <button
                onClick={() => {
                  setSelectedLog(null);
                  setVerificationResult(null);
                }}
                className="text-slate-500 hover:text-slate-350 text-xs font-bold uppercase cursor-pointer"
              >
                Close
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-6">
              
              {/* Top row summaries */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-[#070b13]/40 p-3 rounded-xl border border-slate-850/60">
                  <span className="text-[9px] text-slate-500 font-bold block mb-1">TIMESTAMP</span>
                  <span className="text-xs font-mono font-semibold text-slate-300">
                    {new Date(selectedLog.timestamp).toLocaleString()}
                  </span>
                </div>
                <div className="bg-[#070b13]/40 p-3 rounded-xl border border-slate-850/60">
                  <span className="text-[9px] text-slate-500 font-bold block mb-1">USER</span>
                  <span className="text-xs font-semibold text-slate-300">
                    {selectedLog.username || selectedLog.user_id || 'System'}
                  </span>
                </div>
                <div className="bg-[#070b13]/40 p-3 rounded-xl border border-slate-850/60">
                  <span className="text-[9px] text-slate-500 font-bold block mb-1">ACTION / SERVICE</span>
                  <span className="text-xs font-semibold text-sky-405">
                    {selectedLog.action} ({selectedLog.service_name})
                  </span>
                </div>
                <div className="bg-[#070b13]/40 p-3 rounded-xl border border-slate-850/60">
                  <span className="text-[9px] text-slate-500 font-bold block mb-1">STATUS / IP</span>
                  <span className="text-xs font-semibold text-slate-300">
                    {selectedLog.status} ({selectedLog.ip_address || '-'})
                  </span>
                </div>
              </div>

              {/* Endpoint row */}
              <div className="bg-[#070b13]/40 p-3 rounded-xl border border-slate-850/60">
                <span className="text-[9px] text-slate-500 font-bold block mb-1">API ENDPOINT</span>
                <span className="text-xs font-mono text-slate-300">{selectedLog.endpoint || 'Internal Execution / Background worker'}</span>
              </div>

              {/* Hashing Provenance Block */}
              <div className="space-y-2">
                <div className="flex items-center space-x-1.5 text-xs font-bold text-slate-400">
                  <Layers className="h-4 w-4 text-teal-400" />
                  <span>Cryptographic Chain Signatures</span>
                </div>
                <div className="bg-[#070b13] p-4 rounded-xl border border-slate-850 space-y-3">
                  <div>
                    <span className="text-[9px] text-slate-500 font-bold block">PREVIOUS BLOCK HASH</span>
                    <span className="text-[10px] font-mono text-slate-400 break-all select-all">
                      {selectedLog.previous_hash || '0000000000000000000000000000000000000000000000000000000000000000 (GENESIS BLOCK)'}
                    </span>
                  </div>
                  <div>
                    <span className="text-[9px] text-slate-500 font-bold block">CURRENT BLOCK HASH</span>
                    <span className="text-[10px] font-mono text-sky-400 break-all select-all">
                      {selectedLog.hash}
                    </span>
                  </div>
                </div>
              </div>

              {/* Details Json */}
              <div className="space-y-2">
                <div className="flex items-center space-x-1.5 text-xs font-bold text-slate-400">
                  <FileText className="h-4 w-4 text-sky-400" />
                  <span>Payload Metadata & Context Details</span>
                </div>
                <pre className="bg-[#070b13] p-4 rounded-xl border border-slate-850 text-[10px] font-mono text-slate-300 overflow-x-auto max-h-[150px]">
                  {selectedLog.details_json 
                    ? JSON.stringify(JSON.parse(selectedLog.details_json), null, 2)
                    : '{}'
                  }
                </pre>
              </div>

              {/* verification outcome area */}
              {verificationResult && (
                <div className={`p-4 rounded-xl border flex items-start space-x-3 ${
                  verificationResult.is_valid 
                    ? 'bg-emerald-950/40 border-emerald-500/20 text-emerald-450' 
                    : 'bg-rose-950/40 border-rose-500/20 text-rose-450'
                }`}>
                  {verificationResult.is_valid 
                    ? <CheckCircle2 className="h-5 w-5 mt-0.5 text-emerald-400" /> 
                    : <XCircle className="h-5 w-5 mt-0.5 text-rose-400" />
                  }
                  <div className="text-xs space-y-1">
                    <p className="font-bold text-slate-200">
                      {verificationResult.is_valid ? 'Verification Passed' : 'Verification Failed'}
                    </p>
                    <p className="text-slate-400">{verificationResult.message}</p>
                    <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2 text-[10px] font-mono bg-slate-950/50 p-2.5 rounded border border-slate-900/50">
                      <div>
                        <span className="text-[9px] text-slate-500 block">CALCULATED</span>
                        <span className="break-all">{verificationResult.calculated_hash}</span>
                      </div>
                      <div>
                        <span className="text-[9px] text-slate-500 block">STORED DATABASE</span>
                        <span className="break-all">{verificationResult.database_hash}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-850 flex justify-between bg-[#070b13]/60">
              <button
                onClick={() => handleVerify(selectedLog.id)}
                disabled={verifying}
                className="bg-sky-500 hover:bg-sky-600 disabled:bg-sky-700 text-white font-bold py-1.5 px-4 rounded-lg text-xs shadow-md transition-colors cursor-pointer"
              >
                {verifying ? 'Running Verify...' : 'Verify Cryptographic Integrity'}
              </button>
              <button
                onClick={() => {
                  setSelectedLog(null);
                  setVerificationResult(null);
                }}
                className="border border-slate-800 hover:border-slate-700 text-slate-450 text-xs font-bold px-4 py-1.5 rounded-lg cursor-pointer"
              >
                Dismiss
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
