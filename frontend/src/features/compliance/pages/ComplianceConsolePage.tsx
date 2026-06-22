import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../../services/api';
import { AgGridReact } from 'ag-grid-react';
import { ClientSideRowModelModule } from 'ag-grid-community';
import _createPlotlyComponent from 'react-plotly.js/factory';
import Plotly from 'plotly.js-dist-min';

const createPlotlyComponent = typeof _createPlotlyComponent === 'function'
  ? _createPlotlyComponent
  : (_createPlotlyComponent as any).default;

const Plot = createPlotlyComponent(Plotly);
import { ReactFlow, MiniMap, Controls, Background } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { 
  ShieldCheck, 
  ShieldAlert, 
  History, 
  FileSignature, 
  LineChart, 
  GitBranch, 
  RefreshCw, 
  CheckCircle 
} from 'lucide-react';

export const ComplianceConsolePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'audit' | 'signatures' | 'activity' | 'lineage'>('overview');
  
  // States
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [signatures, setSignatures] = useState<any[]>([]);
  const [lineageNodes, setLineageNodes] = useState<any[]>([]);
  const [lineageEdges, setLineageEdges] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [integrityStatus, setIntegrityStatus] = useState<{ verified: boolean; checked: boolean; error?: string }>({
    verified: false,
    checked: false
  });

  // Fetch data
  const fetchData = async () => {
    setIsLoading(true);
    try {
      const logsData = await apiRequest('/audit/logs?limit=200', { service: 'audit' });
      setAuditLogs(logsData);

      const sigsData = await apiRequest('/compliance/signatures', { service: 'audit' });
      // Flatten signatures for display
      const flattened = sigsData.flatMap((sig: any) => 
        sig.events.map((ev: any) => ({
          id: ev.id,
          sigId: sig.id,
          username: sig.username,
          action_type: ev.action_type,
          entity_id: ev.entity_id,
          reason: ev.reason,
          meaning: ev.meaning,
          timestamp: ev.timestamp,
          hash: sig.signature_hash
        }))
      );
      setSignatures(flattened);

      const graphData = await apiRequest('/lineage/graph', { service: 'lineage' });
      setLineageNodes(graphData.nodes || []);
      setLineageEdges(graphData.edges || []);
    } catch (err) {
      console.error('Failed to load compliance details:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Ledger Integrity check
  const verifyIntegrity = async () => {
    try {
      // Fetch latest log entry
      if (auditLogs.length === 0) {
        setIntegrityStatus({ verified: true, checked: true });
        return;
      }
      const latestId = auditLogs[0].id;
      const res = await apiRequest(`/audit/logs/${latestId}/verify`, { service: 'audit' });
      setIntegrityStatus({
        verified: res.verified,
        checked: true
      });
    } catch (err: any) {
      setIntegrityStatus({
        verified: false,
        checked: true,
        error: err.message || 'Verification execution failed.'
      });
    }
  };

  // AG Grid config
  const auditColDefs = [
    { field: 'timestamp', headerName: 'Timestamp', sortable: true, filter: true, width: 200 },
    { field: 'username', headerName: 'User', sortable: true, filter: true },
    { field: 'action', headerName: 'Action', sortable: true, filter: true },
    { field: 'service_name', headerName: 'Service', sortable: true, filter: true },
    { field: 'endpoint', headerName: 'API Route', sortable: true, filter: true },
    { field: 'status', headerName: 'Status', sortable: true, filter: true, 
      cellRenderer: (p: any) => (
        <span className={`px-2 py-0.5 rounded text-xs ${p.value === 'SUCCESS' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-red-500/20 text-red-300 border border-red-500/30'}`}>
          {p.value}
        </span>
      )
    },
    { field: 'hash', headerName: 'Block Hash', width: 220, 
      cellRenderer: (p: any) => <code className="text-xs text-blue-300 font-mono">{p.value.substring(0, 16)}...</code>
    }
  ];

  const sigColDefs = [
    { field: 'timestamp', headerName: 'Timestamp', sortable: true, filter: true, width: 200 },
    { field: 'username', headerName: 'Signer', sortable: true, filter: true },
    { field: 'action_type', headerName: 'Operation', sortable: true, filter: true },
    { field: 'entity_id', headerName: 'Entity ID', sortable: true, filter: true },
    { field: 'reason', headerName: 'Reason', sortable: true, filter: true, width: 220 },
    { field: 'meaning', headerName: 'Meaning', sortable: true, filter: true },
    { field: 'hash', headerName: 'Signature Hash', width: 220,
      cellRenderer: (p: any) => <code className="text-xs text-amber-300 font-mono">{p.value.substring(0, 16)}...</code>
    }
  ];

  // Chart computations
  const getChartData = () => {
    const counts: { [key: string]: number } = {};
    auditLogs.forEach((log) => {
      counts[log.action] = (counts[log.action] || 0) + 1;
    });

    return [
      {
        x: Object.keys(counts),
        y: Object.values(counts),
        type: 'bar' as const,
        marker: {
          color: 'rgba(59, 130, 246, 0.6)',
          line: {
            color: 'rgb(59, 130, 246)',
            width: 1.5
          }
        }
      }
    ];
  };

  const getStatusChartData = () => {
    let success = 0;
    let failure = 0;
    auditLogs.forEach((log) => {
      if (log.status === 'SUCCESS') success++;
      else failure++;
    });

    return [
      {
        values: [success, failure],
        labels: ['Success', 'Failure'],
        type: 'pie' as const,
        hole: 0.4,
        marker: {
          colors: ['rgba(16, 185, 129, 0.6)', 'rgba(239, 68, 68, 0.6)']
        }
      }
    ];
  };

  // React Flow computations
  const buildReactFlowElements = () => {
    const nodes: any[] = [];
    const edges: any[] = [];
    
    // Group nodes by type for positioning
    const typeGroups: { [key: string]: any[] } = {};
    lineageNodes.forEach((n) => {
      if (!typeGroups[n.type]) typeGroups[n.type] = [];
      typeGroups[n.type].push(n);
    });

    const columns = ['datasource', 'query', 'dataset', 'analytics', 'visualization', 'export'];
    
    lineageNodes.forEach((n) => {
      const colIndex = columns.indexOf(n.type);
      const x = colIndex !== -1 ? colIndex * 240 + 50 : 200;
      
      const group = typeGroups[n.type] || [];
      const itemIndex = group.indexOf(n);
      const y = itemIndex * 140 + 100;

      nodes.push({
        id: n.id,
        position: { x, y },
        data: { 
          label: (
            <div className="text-left font-sans">
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">{n.type}</div>
              <div className="text-xs font-semibold text-slate-100 mt-0.5">{n.name}</div>
            </div>
          )
        },
        style: {
          background: 'rgba(15, 23, 42, 0.85)',
          border: '1px solid rgba(59, 130, 246, 0.4)',
          borderRadius: '12px',
          padding: '10px 14px',
          width: '200px',
          color: '#fff',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
        }
      });
    });

    lineageEdges.forEach((e) => {
      edges.push({
        id: e.id,
        source: e.source,
        target: e.target,
        animated: true,
        style: { stroke: 'rgb(59, 130, 246)', strokeWidth: 2 }
      });
    });

    return { nodes, edges };
  };

  const flowElements = buildReactFlowElements();

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-700/60 pb-5">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
            Compliance & Governance Console
          </h1>
          <p className="text-sm text-slate-400">
            System logs, cryptographic audit verification, electronic signatures, and data lineage mapping.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={fetchData} 
            className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700/60 rounded-lg text-xs font-medium text-slate-300 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh Data
          </button>
          <button 
            onClick={verifyIntegrity} 
            className="flex items-center gap-2 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-xs font-medium text-slate-100 transition-colors shadow-lg shadow-blue-500/20"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            Verify Database Integrity
          </button>
        </div>
      </div>

      {/* Tabs bar */}
      <div className="flex gap-2 border-b border-slate-800 pb-px">
        {[
          { id: 'overview', label: 'Overview', icon: CheckCircle },
          { id: 'audit', label: 'Cryptographic Logs', icon: History },
          { id: 'signatures', label: 'E-Signatures', icon: FileSignature },
          { id: 'activity', label: 'User Activity', icon: LineChart },
          { id: 'lineage', label: 'Data Lineage', icon: GitBranch }
        ].map((t) => {
          const Icon = t.icon;
          const active = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              className={`flex items-center gap-2 px-4 py-2.5 border-b-2 text-sm font-medium transition-all ${active ? 'border-blue-500 text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
            >
              <Icon className="w-4 h-4" />
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Main Tabs Content */}
      <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-md min-h-[500px]">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Integrity Status Card */}
            <div className={`p-5 rounded-2xl border flex items-center justify-between ${integrityStatus.checked ? (integrityStatus.verified ? 'bg-emerald-500/5 border-emerald-500/25' : 'bg-red-500/5 border-red-500/25') : 'bg-slate-800/20 border-slate-700/40'}`}>
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-xl ${integrityStatus.checked ? (integrityStatus.verified ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400') : 'bg-slate-700/20 text-slate-400'}`}>
                  {integrityStatus.checked ? (
                    integrityStatus.verified ? <ShieldCheck className="w-8 h-8" /> : <ShieldAlert className="w-8 h-8 animate-bounce" />
                  ) : (
                    <ShieldCheck className="w-8 h-8 opacity-60" />
                  )}
                </div>
                <div>
                  <h3 className="font-semibold text-slate-100 text-base">
                    {!integrityStatus.checked ? 'Ledger Chain Verification Status' : (integrityStatus.verified ? 'Cryptographic Ledger Verified' : 'Cryptographic Ledger CORRUPTED')}
                  </h3>
                  <p className="text-xs text-slate-400 mt-1 max-w-xl">
                    {!integrityStatus.checked 
                      ? 'Perform an on-demand verification of the SHA-256 block chain to assert that no audit logs have been modified.' 
                      : (integrityStatus.verified 
                        ? 'All ledger entries have been checked sequentially. Cryptographic provenance verified: No modifications detected.'
                        : `Ledger verification failed! Detected broken link or block data mismatch. ${integrityStatus.error || ''}`)}
                  </p>
                </div>
              </div>
              <button 
                onClick={verifyIntegrity}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700/60 rounded-xl text-xs font-semibold text-slate-200 transition-colors"
              >
                {!integrityStatus.checked ? 'Run Verification' : 'Re-verify'}
              </button>
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              <div className="bg-slate-800/20 border border-slate-800 p-5 rounded-2xl">
                <h4 className="text-xs text-slate-400 font-bold uppercase tracking-wider">Audit Trail Records</h4>
                <p className="text-3xl font-bold text-slate-100 mt-2">{auditLogs.length}</p>
                <div className="text-[10px] text-emerald-400 mt-1 flex items-center gap-1">
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                  Active collection logging
                </div>
              </div>
              <div className="bg-slate-800/20 border border-slate-800 p-5 rounded-2xl">
                <h4 className="text-xs text-slate-400 font-bold uppercase tracking-wider">Electronic Signatures</h4>
                <p className="text-3xl font-bold text-slate-100 mt-2">{signatures.length}</p>
                <div className="text-[10px] text-slate-400 mt-1">
                  Double-factor auth signed
                </div>
              </div>
              <div className="bg-slate-800/20 border border-slate-800 p-5 rounded-2xl">
                <h4 className="text-xs text-slate-400 font-bold uppercase tracking-wider">Lineage Trace Elements</h4>
                <p className="text-3xl font-bold text-slate-100 mt-2">{lineageNodes.length + lineageEdges.length}</p>
                <div className="text-[10px] text-blue-400 mt-1">
                  Active flow graph tracked
                </div>
              </div>
            </div>

            {/* Recent Alerts */}
            <div className="bg-slate-800/10 border border-slate-800/60 rounded-2xl p-5">
              <h4 className="text-sm font-semibold text-slate-200 mb-3">Compliance Alert Dashboard</h4>
              <div className="space-y-3">
                <div className="p-3 bg-blue-500/5 border border-blue-500/10 rounded-xl flex justify-between items-center text-xs">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-blue-400" />
                    <span>Central Audit microservice initialized with tamper-evident chain verification.</span>
                  </div>
                  <span className="text-slate-500">System</span>
                </div>
                <div className="p-3 bg-emerald-500/5 border border-emerald-500/10 rounded-xl flex justify-between items-center text-xs">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    <span>Electronic Signatures DB models registered. Double-factor verification enabled.</span>
                  </div>
                  <span className="text-slate-500">Part 11</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'audit' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-base font-semibold text-slate-200">Cryptographic SHA-256 Audit Trail Ledger</h3>
              <span className="text-xs text-slate-400">Total {auditLogs.length} blocks recorded</span>
            </div>
            <div className="ag-theme-alpine-dark w-full h-[450px]">
              <AgGridReact
                rowData={auditLogs}
                columnDefs={auditColDefs}
                modules={[ClientSideRowModelModule]}
                pagination={true}
                paginationPageSize={10}
              />
            </div>
          </div>
        )}

        {activeTab === 'signatures' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-base font-semibold text-slate-200">Electronic Signatures Ledger (FDA 21 CFR Part 11)</h3>
              <span className="text-xs text-slate-400">Total {signatures.length} operations signed</span>
            </div>
            <div className="ag-theme-alpine-dark w-full h-[450px]">
              <AgGridReact
                rowData={signatures}
                columnDefs={sigColDefs}
                modules={[ClientSideRowModelModule]}
                pagination={true}
                paginationPageSize={10}
              />
            </div>
          </div>
        )}

        {activeTab === 'activity' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-slate-800/10 border border-slate-800/80 rounded-2xl p-4">
              <h4 className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-4">Operations Breakdown</h4>
              <div className="flex justify-center">
                {auditLogs.length > 0 ? (
                  <Plot
                    data={getChartData()}
                    layout={{
                      width: 500,
                      height: 380,
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#94a3b8' },
                      xaxis: { gridcolor: '#334155' },
                      yaxis: { gridcolor: '#334155' }
                    }}
                  />
                ) : (
                  <div className="py-20 text-slate-500 text-sm">No activity logged yet.</div>
                )}
              </div>
            </div>

            <div className="bg-slate-800/10 border border-slate-800/80 rounded-2xl p-4">
              <h4 className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-4">Operation Status Mix</h4>
              <div className="flex justify-center">
                {auditLogs.length > 0 ? (
                  <Plot
                    data={getStatusChartData()}
                    layout={{
                      width: 500,
                      height: 380,
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#94a3b8' }
                    }}
                  />
                ) : (
                  <div className="py-20 text-slate-500 text-sm">No status logs recorded.</div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'lineage' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-base font-semibold text-slate-200">Interactive Data Lineage Explorer</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Tracks flow: Datasources → Queries → Datasets → Analytics → Visualization → Export.
              </p>
            </div>
            
            <div className="w-full h-[550px] bg-slate-950/60 border border-slate-800/80 rounded-2xl overflow-hidden relative">
              {flowElements.nodes.length > 0 ? (
                <ReactFlow
                  nodes={flowElements.nodes}
                  edges={flowElements.edges}
                  fitView
                >
                  <MiniMap nodeStrokeWidth={3} zoomable pannable />
                  <Controls />
                  <Background color="#334155" gap={16} />
                </ReactFlow>
              ) : (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500 text-sm gap-2">
                  <GitBranch className="w-10 h-10 text-slate-600 animate-pulse" />
                  <span>No data lineage traces recorded yet.</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
