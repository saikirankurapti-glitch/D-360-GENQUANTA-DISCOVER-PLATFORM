import { useState, useEffect, useMemo, useCallback } from 'react';
import { 
  ReactFlow, 
  Background, 
  Controls, 
  MiniMap, 
  useNodesState, 
  useEdgesState, 
  addEdge,
  MarkerType
} from '@xyflow/react';
import type { Connection } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { 
  Play, 
  Save, 
  Trash2, 
  Settings, 
  History, 
  BarChart3, 
  Mail, 
  Database, 
  FileSpreadsheet, 
  Search, 
  Activity, 
  UserCheck 
} from 'lucide-react';

// Custom Node component inside the same file for clean structure and build compatibility
const CustomWorkflowNode = ({ data, selected }: { data: any, selected: boolean }) => {
  const nodeIcons: Record<string, any> = {
    datasource: Database,
    sync: Activity,
    query: Search,
    compound_search: Search,
    sequence_analysis: Search,
    assay_analysis: Activity,
    export: FileSpreadsheet,
    notification: Mail,
    approval: UserCheck,
  };

  const Icon = nodeIcons[data.type] || Settings;

  const bgColors: Record<string, string> = {
    datasource: 'from-blue-600/25 to-blue-900/10 border-blue-500/40 text-blue-300',
    sync: 'from-emerald-600/25 to-emerald-900/10 border-emerald-500/40 text-emerald-300',
    query: 'from-sky-600/25 to-sky-900/10 border-sky-500/40 text-sky-300',
    compound_search: 'from-indigo-600/25 to-indigo-900/10 border-indigo-500/40 text-indigo-300',
    sequence_analysis: 'from-violet-600/25 to-violet-900/10 border-violet-500/40 text-violet-300',
    assay_analysis: 'from-pink-600/25 to-pink-900/10 border-pink-500/40 text-pink-300',
    export: 'from-amber-600/25 to-amber-900/10 border-amber-500/40 text-amber-300',
    notification: 'from-purple-600/25 to-purple-900/10 border-purple-500/40 text-purple-300',
    approval: 'from-rose-600/25 to-rose-900/10 border-rose-500/40 text-rose-300',
  };

  const bgStyle = bgColors[data.type] || 'from-slate-700/25 to-slate-900/10 border-slate-600/40 text-slate-300';

  return (
    <div className={`p-3 rounded-xl border-2 bg-gradient-to-br ${bgStyle} w-44 shadow-lg backdrop-blur-sm transition-all duration-200 ${
      selected ? 'ring-2 ring-sky-400 border-sky-400 scale-105 shadow-[0_0_15px_rgba(14,165,233,0.3)]' : ''
    }`}>
      <div className="flex items-center space-x-2.5">
        <div className="p-1.5 rounded-lg bg-black/40">
          <Icon className="h-4 w-4" />
        </div>
        <div className="overflow-hidden">
          <p className="text-[10px] font-bold tracking-wider uppercase opacity-65">{data.type}</p>
          <p className="text-xs font-semibold truncate text-white">{data.label}</p>
        </div>
      </div>
    </div>
  );
};

export const WorkflowDesignerPage = () => {
  // Nodes & Edges flow state
  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);
  
  // App UI State
  const [definitions, setDefinitions] = useState<any[]>([]);
  const [selectedDefId, setSelectedDefId] = useState<string>('');
  const [workflowName, setWorkflowName] = useState<string>('');
  const [workflowDesc, setWorkflowDesc] = useState<string>('');
  const [triggerType, setTriggerType] = useState<string>('MANUAL');
  const [cronSchedule, setCronSchedule] = useState<string>('');
  
  const [runs, setRuns] = useState<any[]>([]);
  const [selectedRun, setSelectedRun] = useState<any | null>(null);
  const [runSteps, setRunSteps] = useState<any[]>([]);
  const [approvals, setApprovals] = useState<any[]>([]);
  
  const [activeTab, setActiveTab] = useState<'config' | 'history' | 'approvals' | 'metrics'>('config');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  
  // Electronic Signature Form
  const [signApprover, setSignApprover] = useState<string>('');
  const [signComment, setSignComment] = useState<string>('');
  const [signPassword, setSignPassword] = useState<string>('');
  const [signLoading, setSignLoading] = useState<boolean>(false);
  const [signStatus, setSignStatus] = useState<string | null>(null);

  // Load registered node types mapping
  const nodeTypes = useMemo(() => ({
    custom: CustomWorkflowNode
  }), []);

  // Fetch initial definitions and approvals
  const fetchDefinitions = async () => {
    try {
      const res = await fetch('http://localhost:8009/api/v1/workflows');
      if (res.ok) {
        const data = await res.json();
        setDefinitions(data);
      }
    } catch (err) {
      console.error('Failed to load definitions:', err);
    }
  };

  const fetchRunsAndApprovals = async () => {
    try {
      const runsRes = await fetch('http://localhost:8009/api/v1/workflows/runs');
      if (runsRes.ok) {
        const data = await runsRes.json();
        setRuns(data);
      }
      const appRes = await fetch('http://localhost:8009/api/v1/workflows/approvals');
      if (appRes.ok) {
        const data = await appRes.json();
        setApprovals(data);
      }
    } catch (err) {
      console.error('Failed to load runs/approvals:', err);
    }
  };

  useEffect(() => {
    fetchDefinitions();
    fetchRunsAndApprovals();
    
    const interval = setInterval(() => {
      fetchRunsAndApprovals();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // Sync selected run's steps if open
  useEffect(() => {
    if (selectedRun) {
      const fetchRunSteps = async () => {
        try {
          const res = await fetch(`http://localhost:8009/api/v1/workflows/runs/${selectedRun.id}/steps`);
          if (res.ok) {
            const data = await res.json();
            setRunSteps(data);
          }
        } catch (err) {
          console.error(err);
        }
      };
      fetchRunSteps();
      
      const found = runs.find(r => r.id === selectedRun.id);
      if (found) {
        setSelectedRun(found);
      }
    }
  }, [runs, selectedRun?.id]);

  // Handle edges connection
  const onConnect = useCallback((params: Connection) => {
    setEdges((eds) => addEdge({
      ...params,
      animated: true,
      style: { stroke: '#0ea5e9', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#0ea5e9' }
    }, eds));
  }, [setEdges]);

  // Add a new node to the canvas
  const addNode = (type: string) => {
    const id = `node_${Date.now()}`;
    const defaultData: Record<string, any> = {
      datasource: { label: 'Benchling Ingest', source_id: 1, entity_name: 'experiments', limit: 10 },
      sync: { label: 'Sync Catalog', source_id: 1 },
      query: { label: 'Trino Query', sql: 'SELECT * FROM compounds LIMIT 5' },
      compound_search: { label: 'Cheminfo Search', smiles: 'CCCS(=O)(=O)Nc1ccc(F)c(C(=O)c2c[nH]c3ccc(Cl)cc23)c1F', search_type: 'similarity', threshold: 0.7 },
      sequence_analysis: { label: 'Bioinfo Alignment', sequence_a: 'MADEEKLKIALALGYDAVGD', sequence_b: 'MADEEKIKIALALGYDAVGD' },
      assay_analysis: { label: 'Dose Response Curve', assay_id: 101 },
      export: { label: 'CSV Exporter', format: 'csv' },
      notification: { label: 'Teams Dispatch', channel: 'teams', recipient: 'lab-alert@genquantaa.com', subject: 'Workflow Completed', message: 'Workflow finished executing successfully.' },
      approval: { label: 'Sign Gate', role_required: 'REVIEWER' }
    };

    const newNode = {
      id,
      type: 'custom',
      position: { x: Math.random() * 250 + 50, y: Math.random() * 250 + 50 },
      data: { 
        type, 
        label: defaultData[type]?.label || 'New Step',
        ...defaultData[type] 
      }
    };
    setNodes((nds) => nds.concat(newNode));
    setSelectedNodeId(id);
    setActiveTab('config');
  };

  // Delete node
  const deleteSelectedNode = () => {
    if (!selectedNodeId) return;
    setNodes((nds) => nds.filter((n) => n.id !== selectedNodeId));
    setEdges((eds) => eds.filter((e) => e.source !== selectedNodeId && e.target !== selectedNodeId));
    setSelectedNodeId(null);
  };

  // Node input config update
  const updateNodeDataField = (field: string, val: any) => {
    if (!selectedNodeId) return;
    setNodes((nds) => 
      nds.map((n) => {
        if (n.id === selectedNodeId) {
          return {
            ...n,
            data: { ...n.data, [field]: val }
          };
        }
        return n;
      })
    );
  };

  // Save workflow definition
  const handleSaveWorkflow = async () => {
    if (!workflowName.trim()) {
      alert('Please enter a name for the workflow.');
      return;
    }
    const cleanNodes = nodes.map(n => ({
      id: n.id,
      type: n.data.type,
      position: n.position,
      data: n.data
    }));

    const cleanEdges = edges.map(e => ({
      id: e.id,
      source: e.source,
      target: e.target
    }));

    const payload = {
      name: workflowName,
      description: workflowDesc,
      nodes_json: JSON.stringify(cleanNodes),
      edges_json: JSON.stringify(cleanEdges),
      trigger_type: triggerType,
      cron_schedule: triggerType === 'SCHEDULED' ? cronSchedule : null,
      is_active: true
    };

    try {
      const method = selectedDefId ? 'POST' : 'POST'; // We will create new / trigger updates
      const endpoint = 'http://localhost:8009/api/v1/workflows';
      
      const res = await fetch(endpoint, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        alert('Workflow definition saved successfully.');
        fetchDefinitions();
      } else {
        alert('Error saving workflow.');
      }
    } catch (err) {
      console.error(err);
      alert('Network error while saving workflow.');
    }
  };

  // Load workflow definition
  const handleLoadDefinition = (defIdStr: string) => {
    setSelectedDefId(defIdStr);
    if (!defIdStr) {
      setNodes([]);
      setEdges([]);
      setWorkflowName('');
      setWorkflowDesc('');
      return;
    }
    const def = definitions.find(d => d.id === Number(defIdStr));
    if (def) {
      setWorkflowName(def.name);
      setWorkflowDesc(def.description || '');
      setTriggerType(def.trigger_type);
      setCronSchedule(def.cron_schedule || '');
      
      const parsedNodes = JSON.parse(def.nodes_json || '[]').map((n: any) => ({
        id: n.id,
        type: 'custom',
        position: n.position || { x: 100, y: 100 },
        data: n.data || { type: n.type, label: n.type }
      }));
      
      const parsedEdges = JSON.parse(def.edges_json || '[]').map((e: any) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        animated: true,
        style: { stroke: '#0ea5e9', strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#0ea5e9' }
      }));

      setNodes(parsedNodes);
      setEdges(parsedEdges);
    }
  };

  // Launch a manual execution run
  const handleLaunchRun = async () => {
    if (!selectedDefId) {
      alert('Please save/load a workflow definition first.');
      return;
    }
    try {
      const res = await fetch(`http://localhost:8009/api/v1/workflows/${selectedDefId}/run`, {
        method: 'POST'
      });
      if (res.ok) {
        const runData = await res.json();
        setSelectedRun(runData);
        setActiveTab('history');
        fetchRunsAndApprovals();
      } else {
        alert('Failed to launch workflow run.');
      }
    } catch (err) {
      console.error(err);
      alert('Error triggering execution.');
    }
  };

  // Execute Part 11 Electronic Signature Approval
  const handleActionApproval = async (approvalId: number, status: 'APPROVED' | 'REJECTED') => {
    if (!signApprover.trim() || !signPassword.trim()) {
      alert('Approver username and password PIN proof are required for Part 11 validation.');
      return;
    }
    setSignLoading(true);
    setSignStatus(null);

    const payload = {
      status,
      approved_by: signApprover,
      comment: signComment,
      signature_payload: {
        user_id: 102,
        signed_fullname: signApprover,
        password_hash: `sha256_hashed_${signPassword}`
      }
    };

    try {
      const res = await fetch(`http://localhost:8009/api/v1/workflows/approvals/${approvalId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setSignStatus('Signature stored and verified. Resuming workflow...');
        setSignApprover('');
        setSignComment('');
        setSignPassword('');
        setTimeout(() => {
          setSignStatus(null);
          fetchRunsAndApprovals();
        }, 3000);
      } else {
        setSignStatus('Signature verification failed.');
      }
    } catch (err) {
      console.error(err);
      setSignStatus('Network error during signature action.');
    } finally {
      setSignLoading(false);
    }
  };

  const selectedNode = nodes.find(n => n.id === selectedNodeId);

  // Workflow Metrics compilation
  const metrics = useMemo(() => {
    const total = runs.length;
    const completed = runs.filter(r => r.status === 'COMPLETED').length;
    const failed = runs.filter(r => r.status === 'FAILED').length;
    const pending = runs.filter(r => r.status === 'PENDING' || r.status === 'RUNNING' || r.status === 'WAITING_APPROVAL').length;
    const rate = total > 0 ? ((completed / total) * 100).toFixed(1) : '0';
    return { total, completed, failed, pending, successRate: rate };
  }, [runs]);

  return (
    <div className="flex-1 flex flex-col space-y-6 h-full select-none">
      
      {/* Top Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-[#0c1220] border border-[#1e293b] p-4 rounded-2xl flex-shrink-0">
        <div className="flex items-center space-x-3">
          <Database className="h-5 w-5 text-sky-400" />
          <select
            value={selectedDefId}
            onChange={(e) => handleLoadDefinition(e.target.value)}
            className="bg-[#070b13] border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-xl focus:border-sky-500 focus:outline-none w-56 cursor-pointer"
          >
            <option value="">-- Create New Workflow --</option>
            {definitions.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name} ({d.trigger_type})
              </option>
            ))}
          </select>
        </div>

        {/* Workflow Meta settings */}
        <div className="flex flex-1 max-w-lg mx-4 space-x-3">
          <input
            type="text"
            placeholder="Workflow Name..."
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            className="bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 flex-1"
          />
          <input
            type="text"
            placeholder="Description..."
            value={workflowDesc}
            onChange={(e) => setWorkflowDesc(e.target.value)}
            className="bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 flex-1"
          />
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          <button
            onClick={handleSaveWorkflow}
            className="flex items-center space-x-1.5 bg-sky-500 hover:bg-sky-600 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-[0_4px_15px_rgba(14,165,233,0.3)] transition-colors cursor-pointer"
          >
            <Save className="h-3.5 w-3.5" />
            <span>Save Workflow</span>
          </button>
          <button
            onClick={handleLaunchRun}
            disabled={!selectedDefId}
            className="flex items-center space-x-1.5 bg-emerald-500 hover:bg-emerald-600 disabled:opacity-40 disabled:pointer-events-none text-white px-4 py-2 rounded-xl text-xs font-bold shadow-[0_4px_15px_rgba(16,185,129,0.3)] transition-colors cursor-pointer"
          >
            <Play className="h-3.5 w-3.5" />
            <span>Run Workflow</span>
          </button>
        </div>
      </div>

      {/* Main Grid Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[560px] flex-1 min-h-0">
        
        {/* Left Toolbar: Node Types Selector */}
        <div className="glass-panel border border-slate-800 rounded-2xl p-5 flex flex-col justify-between space-y-6">
          <div className="space-y-4 overflow-y-auto max-h-[500px]">
            <h4 className="font-bold text-white text-sm border-b border-slate-850 pb-2">Workflow Nodes</h4>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Click to add step</p>
            
            <div className="space-y-2.5">
              {[
                { type: 'datasource', title: 'Data Ingest', desc: 'Query LIMS/ELN active source', color: 'hover:border-blue-500/40 text-blue-400 bg-blue-500/5' },
                { type: 'sync', title: 'Catalog Sync', desc: 'Synchronize connector entities', color: 'hover:border-emerald-500/40 text-emerald-400 bg-emerald-500/5' },
                { type: 'query', title: 'Trino SQL Query', desc: 'Perform analytics query execution', color: 'hover:border-sky-500/40 text-sky-400 bg-sky-500/5' },
                { type: 'compound_search', title: 'Molecular Search', desc: 'Smiles similarity & SAR', color: 'hover:border-indigo-500/40 text-indigo-400 bg-indigo-500/5' },
                { type: 'sequence_analysis', title: 'Bioinfo Alignment', desc: 'Pairwise sequence analysis', color: 'hover:border-violet-500/40 text-violet-400 bg-violet-500/5' },
                { type: 'assay_analysis', title: 'Assay Curve Fitting', desc: 'Hill equation response calculations', color: 'hover:border-pink-500/40 text-pink-400 bg-pink-500/5' },
                { type: 'export', title: 'CSV Exporter', desc: 'Format upstream data to file', color: 'hover:border-amber-500/40 text-amber-400 bg-amber-500/5' },
                { type: 'notification', title: 'Dispatch Alert', desc: 'Email/Teams notification alerts', color: 'hover:border-purple-500/40 text-purple-400 bg-purple-500/5' },
                { type: 'approval', title: 'Signature Approval Gate', desc: 'Part 11 compliance approval gate', color: 'hover:border-rose-500/40 text-rose-400 bg-rose-500/5' }
              ].map((btn) => (
                <button
                  key={btn.type}
                  onClick={() => addNode(btn.type)}
                  className={`w-full flex flex-col p-3 border border-slate-800 rounded-xl transition-all cursor-pointer group text-left ${btn.color}`}
                >
                  <p className="text-xs font-bold text-white group-hover:text-sky-400">{btn.title}</p>
                  <p className="text-[9px] text-slate-500 mt-0.5">{btn.desc}</p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Central Canvas */}
        <div className="lg:col-span-2 h-full flex flex-col overflow-hidden relative">
          <div className="h-full w-full bg-[#070b13] rounded-2xl border border-slate-800 overflow-hidden relative shadow-[0_4px_30px_rgba(0,0,0,0.5)]">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              nodeTypes={nodeTypes}
              fitView
              onPaneClick={() => setSelectedNodeId(null)}
              onNodeClick={(_, node) => setSelectedNodeId(node.id)}
            >
              <Background color="#1e293b" gap={16} size={1} />
              <Controls className="!bg-[#0c1220] !border-slate-800 !text-slate-300" />
              <MiniMap
                nodeStrokeColor="#0ea5e9"
                nodeColor="#0c1220"
                className="!bg-[#0c1220] !border-slate-800"
                maskColor="rgba(7, 11, 19, 0.7)"
              />
            </ReactFlow>
            <div className="absolute top-4 left-4 bg-[#0c1220]/90 border border-slate-800 px-4 py-2.5 rounded-xl text-[10px] text-slate-400 max-w-xs space-y-1 pointer-events-none backdrop-blur">
              <p className="font-bold text-white uppercase tracking-wider">Workflow Canvas</p>
              <p>• Select nodes from left menu to add steps.</p>
              <p>• Draw arrows between output and input handles.</p>
              <p>• Click a node to view config panel.</p>
            </div>
          </div>
        </div>

        {/* Right Sidebar: Config, Runs, E-Signatures, Metrics */}
        <div className="glass-panel border border-slate-800 rounded-2xl p-5 flex flex-col h-full overflow-hidden shadow-[0_8px_30px_rgba(0,0,0,0.3)]">
          
          {/* Tab buttons */}
          <div className="flex border-b border-slate-850 pb-3 gap-2 flex-shrink-0">
            {[
              { id: 'config', label: 'Settings', icon: Settings },
              { id: 'history', label: 'History', icon: History },
              { id: 'approvals', label: 'Signatures', icon: UserCheck },
              { id: 'metrics', label: 'Metrics', icon: BarChart3 }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold cursor-pointer transition-colors ${
                    activeTab === tab.id 
                      ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20' 
                      : 'text-slate-400 hover:text-slate-200 hover:bg-[#131b2e]'
                  }`}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>

          <div className="flex-1 overflow-y-auto mt-4 min-h-0 text-slate-200 space-y-4">
            
            {/* Tab: Settings */}
            {activeTab === 'config' && (
              <div className="space-y-4">
                {selectedNode ? (
                  <div className="space-y-3.5">
                    <div className="flex justify-between items-center">
                      <h5 className="text-xs font-bold text-sky-400 uppercase tracking-wider">{selectedNode.data.type} Config</h5>
                      <button
                        onClick={deleteSelectedNode}
                        className="text-rose-400 hover:text-rose-300 p-1 hover:bg-rose-500/5 rounded transition-all cursor-pointer"
                        title="Delete node"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>

                    <div>
                      <label className="text-[10px] text-slate-500 font-bold uppercase block mb-1">Step Name</label>
                      <input
                        type="text"
                        value={selectedNode.data.label}
                        onChange={(e) => updateNodeDataField('label', e.target.value)}
                        className="bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 w-full"
                      />
                    </div>

                    {/* Node Specific Fields */}
                    {selectedNode.data.type === 'datasource' && (
                      <div className="space-y-3">
                        <div>
                          <label className="text-[10px] text-slate-500 font-bold uppercase block mb-1">Source ID</label>
                          <input
                            type="number"
                            value={selectedNode.data.source_id || 1}
                            onChange={(e) => updateNodeDataField('source_id', Number(e.target.value))}
                            className="bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 w-full"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] text-slate-500 font-bold uppercase block mb-1">Entity Name</label>
                          <input
                            type="text"
                            value={selectedNode.data.entity_name || 'experiments'}
                            onChange={(e) => updateNodeDataField('entity_name', e.target.value)}
                            className="bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 w-full"
                          />
                        </div>
                      </div>
                    )}

                    {selectedNode.data.type === 'query' && (
                      <div>
                        <label className="text-[10px] text-slate-500 font-bold uppercase block mb-1">SQL Script</label>
                        <textarea
                          rows={4}
                          value={selectedNode.data.sql || ''}
                          onChange={(e) => updateNodeDataField('sql', e.target.value)}
                          className="bg-[#070b13] border border-slate-800 text-xs text-emerald-400 font-mono p-3 rounded-xl focus:outline-none focus:border-sky-500 w-full"
                        />
                      </div>
                    )}

                    {selectedNode.data.type === 'compound_search' && (
                      <div className="space-y-3">
                        <div>
                          <label className="text-[10px] text-slate-500 font-bold uppercase block mb-1">SMILES String</label>
                          <input
                            type="text"
                            value={selectedNode.data.smiles || ''}
                            onChange={(e) => updateNodeDataField('smiles', e.target.value)}
                            className="bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 w-full"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] text-slate-500 font-bold uppercase block mb-1">Search Type</label>
                          <select
                            value={selectedNode.data.search_type || 'similarity'}
                            onChange={(e) => updateNodeDataField('search_type', e.target.value)}
                            className="bg-[#070b13] border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-xl focus:outline-none w-full"
                          >
                            <option value="similarity">Tanimoto Similarity</option>
                            <option value="substructure">Substructure Match</option>
                            <option value="exact">Exact Search</option>
                          </select>
                        </div>
                        <div>
                          <label className="text-[10px] text-slate-500 font-bold uppercase block mb-1">Similarity Threshold</label>
                          <input
                            type="number"
                            step="0.05"
                            value={selectedNode.data.threshold || 0.7}
                            onChange={(e) => updateNodeDataField('threshold', Number(e.target.value))}
                            className="bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 w-full"
                          />
                        </div>
                      </div>
                    )}

                    {selectedNode.data.type === 'notification' && (
                      <div className="space-y-3">
                        <div>
                          <label className="text-[10px] text-slate-500 font-bold uppercase block mb-1">Recipient</label>
                          <input
                            type="email"
                            value={selectedNode.data.recipient || ''}
                            onChange={(e) => updateNodeDataField('recipient', e.target.value)}
                            className="bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 w-full"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] text-slate-500 font-bold uppercase block mb-1">Message Body</label>
                          <textarea
                            rows={3}
                            value={selectedNode.data.message || ''}
                            onChange={(e) => updateNodeDataField('message', e.target.value)}
                            className="bg-[#070b13] border border-slate-800 text-xs text-slate-200 p-3 rounded-xl focus:outline-none focus:border-sky-500 w-full"
                          />
                        </div>
                      </div>
                    )}

                    {selectedNode.data.type === 'approval' && (
                      <div>
                        <label className="text-[10px] text-slate-500 font-bold uppercase block mb-1">Role Required</label>
                        <select
                          value={selectedNode.data.role_required || 'REVIEWER'}
                          onChange={(e) => updateNodeDataField('role_required', e.target.value)}
                          className="bg-[#070b13] border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-xl focus:outline-none w-full"
                        >
                          <option value="SCIENTIST">Scientist</option>
                          <option value="REVIEWER">Reviewer</option>
                          <option value="COMPLIANCE">Compliance Officer</option>
                        </select>
                      </div>
                    )}

                  </div>
                ) : (
                  <div className="text-center text-xs text-slate-500 italic py-12">
                    Click a node on the canvas to configure its inputs and parameters
                  </div>
                )}
              </div>
            )}

            {/* Tab: History */}
            {activeTab === 'history' && (
              <div className="space-y-4">
                {selectedRun ? (
                  <div className="space-y-3.5">
                    <div className="flex justify-between items-center border-b border-slate-850 pb-2">
                      <h5 className="text-xs font-bold text-white font-mono">Run #{selectedRun.id} Details</h5>
                      <button
                        onClick={() => setSelectedRun(null)}
                        className="text-xs text-sky-400 hover:text-sky-300 font-semibold cursor-pointer"
                      >
                        Back to List
                      </button>
                    </div>

                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400">Status:</span>
                      <span className={`font-bold px-2 py-0.5 rounded text-[10px] uppercase font-mono ${
                        selectedRun.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                        selectedRun.status === 'FAILED' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                        selectedRun.status === 'WAITING_APPROVAL' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse' :
                        'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                      }`}>{selectedRun.status}</span>
                    </div>

                    {/* Step executions */}
                    <div className="space-y-2">
                      <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Executed Steps</p>
                      {runSteps.map((step) => (
                        <div key={step.id} className="p-3 bg-[#0d1322] border border-slate-800 rounded-xl space-y-1">
                          <div className="flex justify-between items-center">
                            <span className="text-xs font-bold text-white">{step.step_name}</span>
                            <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded uppercase ${
                              step.status === 'COMPLETED' ? 'text-emerald-400 bg-emerald-500/5' :
                              step.status === 'FAILED' ? 'text-rose-400 bg-rose-500/5' :
                              'text-amber-400 bg-amber-500/5'
                            }`}>{step.status}</span>
                          </div>
                          <div className="text-[10px] text-slate-500 font-mono flex justify-between">
                            <span>Type: {step.node_type}</span>
                            <span>Speed: {step.execution_time_ms.toFixed(0)}ms</span>
                          </div>
                          {step.outputs_json && (
                            <pre className="text-[9px] bg-black/30 p-2 rounded text-slate-400 max-h-20 overflow-auto font-mono mt-1">
                              {JSON.stringify(JSON.parse(step.outputs_json), null, 2)}
                            </pre>
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Logs */}
                    <div className="space-y-2">
                      <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Execution Logs</p>
                      <pre className="text-[9px] bg-[#070b13] p-3 border border-slate-800 rounded-xl text-slate-400 font-mono max-h-44 overflow-y-auto whitespace-pre-wrap leading-relaxed select-text">
                        {selectedRun.logs || 'No logs recorded.'}
                      </pre>
                    </div>

                  </div>
                ) : (
                  <div className="space-y-2.5">
                    {runs.length === 0 ? (
                      <p className="text-center text-xs text-slate-500 italic py-12">No execution runs recorded</p>
                    ) : (
                      runs.map((run) => (
                        <button
                          key={run.id}
                          onClick={() => setSelectedRun(run)}
                          className="w-full flex items-center justify-between p-3.5 bg-[#0d1322] hover:bg-[#131b2e] border border-slate-800 hover:border-slate-700 rounded-xl transition-all text-left cursor-pointer group"
                        >
                          <div className="space-y-1">
                            <p className="text-xs font-bold text-white group-hover:text-sky-400">Run #{run.id}</p>
                            <p className="text-[10px] text-slate-500 font-mono">Started: {new Date(run.started_at).toLocaleString()}</p>
                          </div>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded font-mono uppercase ${
                            run.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                            run.status === 'FAILED' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                            run.status === 'WAITING_APPROVAL' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse' :
                            'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                          }`}>{run.status}</span>
                        </button>
                      ))
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Tab: Approvals */}
            {activeTab === 'approvals' && (
              <div className="space-y-4">
                <div className="border-b border-slate-850 pb-2">
                  <h5 className="text-xs font-bold text-white">Pending Electronic Signatures</h5>
                  <p className="text-[10px] text-slate-500 mt-0.5">21 CFR Part 11 validation requires password verification.</p>
                </div>

                {approvals.filter(a => a.status === 'PENDING').length === 0 ? (
                  <p className="text-center text-xs text-slate-500 italic py-12">No pending approval requests</p>
                ) : (
                  approvals.filter(a => a.status === 'PENDING').map((app) => (
                    <div key={app.id} className="p-4 bg-[#0d1322] border border-slate-800 rounded-2xl space-y-4">
                      <div className="flex justify-between items-center text-xs">
                        <span className="font-bold text-white">Run #{app.run_id} Approval</span>
                        <span className="text-[10px] bg-rose-500/10 border border-rose-500/25 text-rose-400 font-bold px-2 py-0.5 rounded uppercase font-mono">{app.role_required}</span>
                      </div>

                      {/* E-sign Credentials Form */}
                      <div className="space-y-3">
                        <div>
                          <label className="text-[10px] text-slate-500 font-bold uppercase block mb-1">Full Name</label>
                          <input
                            type="text"
                            placeholder="e.g. Dr. Sarah Connor"
                            value={signApprover}
                            onChange={(e) => setSignApprover(e.target.value)}
                            className="bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 w-full"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] text-slate-500 font-bold uppercase block mb-1">Comment / Meaning</label>
                          <input
                            type="text"
                            placeholder="e.g. Verified data alignment"
                            value={signComment}
                            onChange={(e) => setSignComment(e.target.value)}
                            className="bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 w-full"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] text-slate-500 font-bold uppercase block mb-1">Password Proof PIN</label>
                          <input
                            type="password"
                            placeholder="••••"
                            value={signPassword}
                            onChange={(e) => setSignPassword(e.target.value)}
                            className="bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 w-full"
                          />
                        </div>
                      </div>

                      {signStatus && (
                        <p className="text-[10px] text-sky-400 font-mono bg-sky-950/20 p-2 rounded border border-sky-500/20">{signStatus}</p>
                      )}

                      <div className="flex gap-2.5">
                        <button
                          disabled={signLoading}
                          onClick={() => handleActionApproval(app.id, 'APPROVED')}
                          className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white font-bold py-2 rounded-xl text-xs transition-colors cursor-pointer disabled:opacity-40"
                        >
                          Approve & Sign
                        </button>
                        <button
                          disabled={signLoading}
                          onClick={() => handleActionApproval(app.id, 'REJECTED')}
                          className="flex-1 bg-rose-500 hover:bg-rose-600 text-white font-bold py-2 rounded-xl text-xs transition-colors cursor-pointer disabled:opacity-40"
                        >
                          Reject Run
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Tab: Metrics */}
            {activeTab === 'metrics' && (
              <div className="space-y-4">
                <div className="border-b border-slate-850 pb-2">
                  <h5 className="text-xs font-bold text-white">Engine Statistics</h5>
                  <p className="text-[10px] text-slate-500 mt-0.5">Real-time metrics tracking workflow execution efficiency.</p>
                </div>

                <div className="grid grid-cols-2 gap-3.5">
                  <div className="p-3 bg-[#0d1322] border border-slate-800 rounded-xl text-center">
                    <p className="text-[10px] text-slate-500 font-bold uppercase">Success Rate</p>
                    <p className="text-xl font-extrabold text-emerald-400 font-mono mt-1">{metrics.successRate}%</p>
                  </div>
                  <div className="p-3 bg-[#0d1322] border border-slate-800 rounded-xl text-center">
                    <p className="text-[10px] text-slate-500 font-bold uppercase">Total Runs</p>
                    <p className="text-xl font-extrabold text-white font-mono mt-1">{metrics.total}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Run Summary</p>
                  <div className="p-3.5 bg-[#0a0f1b] border border-slate-900 rounded-xl text-xs space-y-2">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Completed runs:</span>
                      <span className="font-bold text-emerald-400">{metrics.completed}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Failed runs:</span>
                      <span className="font-bold text-rose-400">{metrics.failed}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Active/Pending:</span>
                      <span className="font-bold text-sky-400">{metrics.pending}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>

      </div>
    </div>
  );
};
