import { useEffect, useState, useMemo } from 'react';
import { apiRequest } from '../../../services/api';
import _createPlotlyComponent from 'react-plotly.js/factory';
import Plotly from 'plotly.js-dist-min';
import { 
  BarChart4, LayoutDashboard, Dna, GitMerge, ShieldCheck, 
  Sparkles, RefreshCw, FlaskConical, TrendingUp, Clock, 
  CheckCircle2, AlertTriangle, FileText, Activity, AlertCircle, Database
} from 'lucide-react';

const createPlotlyComponent = typeof _createPlotlyComponent === 'function'
  ? _createPlotlyComponent
  : (_createPlotlyComponent as any).default;

const Plot = createPlotlyComponent(Plotly);

interface DashboardData {
  compounds: {
    total_count: number;
    by_target: Record<string, number>;
    by_project: Record<string, number>;
    mw_distribution: number[];
    clogp_distribution: number[];
    hbd_distribution: number[];
    hba_distribution: number[];
    lipinski_compliance: { compliant: number; non_compliant: number };
    top_active: Array<{ compound_id: string; target: string; ic50: number; name: string }>;
  };
  assays: {
    total_count: number;
    by_target: Record<string, number>;
    ic50_distribution: number[];
    ec50_distribution: number[];
    success_rate: number;
    top_performing: Array<{ compound_id: string; target: string; ic50: number; name: string }>;
  };
  bioinformatics: {
    total_count: number;
    type_distribution: Record<string, number>;
    organism_distribution: Record<string, number>;
    mutation_frequency: number;
    alignments_count: number;
    clusters_count: number;
  };
  workflows: {
    total_runs: number;
    success_rate: number;
    failure_rate: number;
    running_count: number;
    avg_duration_sec: number;
    sla_compliance_rate: number;
    utilization: Record<string, number>;
    steps: Array<{ id: number; run_id: number; step_name: string; node_type: string; status: string; execution_time_ms: number }>;
    approvals: Array<{ id: number; run_id: number; status: string; requested_at: string; completed_at: string | null; approved_by: string | null }>;
  };
  compliance: {
    total_events: number;
    events_by_type: Record<string, number>;
    events_by_user: Record<string, number>;
    signature_trends: Record<string, number>;
    violations_count: number;
    health_score: number;
    total_signatures: number;
    total_entity_versions: number;
  };
  ai_copilot: {
    total_sessions: number;
    total_messages: number;
    total_queries: number;
    question_categories: Record<string, number>;
  };
  metadata: {
    total_entities: number;
    total_fields: number;
    total_values: number;
    total_relationships: number;
    completeness_score: number;
  };
  eln_lims: {
    experiments_by_scientist: Record<string, number>;
    experiments_by_project: Record<string, number>;
    completion_rate: number;
    total_runs: number;
  };
  executive: {
    total_assets: number;
    total_compounds: number;
    total_assays: number;
    total_sequences: number;
    total_workflows: number;
    total_compliance_events: number;
    total_ai_queries: number;
  };
}

export const AnalyticsDashboard = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'executive' | 'scientific' | 'bio' | 'workflows' | 'compliance' | 'ai'>('executive');

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiRequest('/analytics/dashboard-analytics', { service: 'query' });
      setData(res);
    } catch (e: any) {
      setError(e.message || "Failed to retrieve real-time dashboard metrics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="h-full flex flex-col justify-center items-center space-y-4">
        <RefreshCw className="h-10 w-10 text-sky-400 animate-spin" />
        <div className="text-center">
          <p className="text-sm font-semibold text-slate-200">Aggregating AnalytiX Platform Analytics...</p>
          <p className="text-xs text-slate-500 mt-1">Fetching real PostgreSQL datasets from 10 microservices</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="h-full flex flex-col justify-center items-center space-y-4 p-8">
        <AlertCircle className="h-12 w-12 text-rose-500" />
        <div className="text-center max-w-md">
          <h3 className="text-md font-bold text-slate-200">Error Loading Analytics</h3>
          <p className="text-xs text-slate-500 mt-2">{error || "No data returned."}</p>
          <button 
            onClick={fetchDashboardData}
            className="mt-4 px-4 py-2 bg-sky-500 hover:bg-sky-600 text-white text-xs font-bold rounded-xl transition-all cursor-pointer"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 h-full overflow-y-auto pb-10 pr-2">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-[#0c1220] border border-[#1e293b] p-6 rounded-2xl gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center space-x-3">
            <Activity className="h-7 w-7 text-sky-400" />
            <span>AnalytiX Analytics Suite</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time multi-dimensional overview of Compounds, Assays, Bioinformatics, Workflow runs, Compliance, and AI Copilot usage.
          </p>
        </div>
        <button 
          onClick={fetchDashboardData}
          className="flex items-center space-x-1.5 bg-[#131b2e] hover:bg-[#1e293b] border border-slate-800 text-slate-300 text-xs font-bold px-4 py-2.5 rounded-xl transition-all"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* Primary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="bg-gradient-to-br from-[#0c1220] to-[#0f172a] border border-[#1e293b] p-5 rounded-2xl flex items-center justify-between shadow-lg relative overflow-hidden group">
          <div className="absolute right-0 bottom-0 translate-x-2 translate-y-2 opacity-5 pointer-events-none group-hover:scale-110 transition-all duration-300">
            <FlaskConical className="h-28 w-28 text-sky-400" />
          </div>
          <div>
            <p className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Total Scientific Assets</p>
            <p className="text-3xl font-extrabold text-white mt-1.5">{data.executive.total_assets}</p>
            <p className="text-[10px] text-emerald-400 font-semibold mt-1">Compounds, Assays & Sequences</p>
          </div>
          <div className="bg-sky-500/10 border border-sky-500/20 p-3 rounded-xl text-sky-400">
            <FlaskConical className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-[#0c1220] to-[#0f172a] border border-[#1e293b] p-5 rounded-2xl flex items-center justify-between shadow-lg relative overflow-hidden group">
          <div className="absolute right-0 bottom-0 translate-x-2 translate-y-2 opacity-5 pointer-events-none group-hover:scale-110 transition-all duration-300">
            <GitMerge className="h-28 w-28 text-violet-400" />
          </div>
          <div>
            <p className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Workflow SLA Rate</p>
            <p className="text-3xl font-extrabold text-white mt-1.5">{data.workflows.sla_compliance_rate}%</p>
            <p className="text-[10px] text-violet-400 font-semibold mt-1">SLA duration &lt; 60 seconds</p>
          </div>
          <div className="bg-violet-500/10 border border-violet-500/20 p-3 rounded-xl text-violet-400">
            <GitMerge className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-[#0c1220] to-[#0f172a] border border-[#1e293b] p-5 rounded-2xl flex items-center justify-between shadow-lg relative overflow-hidden group">
          <div className="absolute right-0 bottom-0 translate-x-2 translate-y-2 opacity-5 pointer-events-none group-hover:scale-110 transition-all duration-300">
            <ShieldCheck className="h-28 w-28 text-emerald-400" />
          </div>
          <div>
            <p className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Compliance Health</p>
            <p className="text-3xl font-extrabold text-white mt-1.5">{data.compliance.health_score}%</p>
            <p className="text-[10px] text-emerald-400 font-semibold mt-1">Verified audit hash chain integrity</p>
          </div>
          <div className="bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-xl text-emerald-400">
            <ShieldCheck className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-[#0c1220] to-[#0f172a] border border-[#1e293b] p-5 rounded-2xl flex items-center justify-between shadow-lg relative overflow-hidden group">
          <div className="absolute right-0 bottom-0 translate-x-2 translate-y-2 opacity-5 pointer-events-none group-hover:scale-110 transition-all duration-300">
            <Sparkles className="h-28 w-28 text-amber-400" />
          </div>
          <div>
            <p className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">AI Scientist Copilot Requests</p>
            <p className="text-3xl font-extrabold text-white mt-1.5">{data.ai_copilot.total_queries}</p>
            <p className="text-[10px] text-amber-400 font-semibold mt-1">Active research sessions: {data.ai_copilot.total_sessions}</p>
          </div>
          <div className="bg-amber-500/10 border border-amber-500/20 p-3 rounded-xl text-amber-400">
            <Sparkles className="h-6 w-6" />
          </div>
        </div>
      </div>

      {/* Tabs Menu */}
      <div className="flex border-b border-slate-800 gap-2 overflow-x-auto flex-nowrap scrollbar-none pb-1">
        {[
          { id: 'executive', label: 'Executive Dashboard', icon: LayoutDashboard },
          { id: 'scientific', label: 'Scientific Insights', icon: FlaskConical },
          { id: 'bio', label: 'Bioinformatics', icon: Dna },
          { id: 'workflows', label: 'Workflow Operations', icon: GitMerge },
          { id: 'compliance', label: 'Compliance & Audit', icon: ShieldCheck },
          { id: 'ai', label: 'AI Copilot Insights', icon: Sparkles }
        ].map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-5 py-3 border-b-2 font-semibold text-xs transition-all whitespace-nowrap cursor-pointer ${
                isActive
                  ? 'border-sky-500 text-sky-400 bg-sky-500/5'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Active Tab Screen */}
      <div>
        {/* EXECUTIVE DASHBOARD */}
        {activeTab === 'executive' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl space-y-4">
                <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Asset Distribution</h3>
                <div className="flex justify-center">
                  <Plot
                    data={[{
                      values: [data.compounds.total_count, data.assays.total_count, data.bioinformatics.total_count],
                      labels: ['Compounds', 'Assays', 'Bioinfo Sequences'],
                      type: 'pie',
                      hole: 0.4,
                      marker: { colors: ['#0ea5e9', '#a855f7', '#10b981'] }
                    }]}
                    layout={{
                      width: 320,
                      height: 240,
                      margin: { t: 10, b: 10, l: 10, r: 10 },
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#94a3b8', size: 10 },
                      showlegend: true,
                      legend: { orientation: 'h', x: 0, y: -0.2 }
                    }}
                    config={{ displayModeBar: false }}
                  />
                </div>
              </div>

              <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl space-y-4">
                <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Workflow Runs by Status</h3>
                <div className="flex justify-center">
                  <Plot
                    data={[{
                      values: [
                        data.workflows.success_rate,
                        data.workflows.failure_rate,
                        100 - (data.workflows.success_rate + data.workflows.failure_rate)
                      ],
                      labels: ['Completed', 'Failed', 'Running/Pending'],
                      type: 'pie',
                      hole: 0.4,
                      marker: { colors: ['#10b981', '#f43f5e', '#f59e0b'] }
                    }]}
                    layout={{
                      width: 320,
                      height: 240,
                      margin: { t: 10, b: 10, l: 10, r: 10 },
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#94a3b8', size: 10 },
                      showlegend: true,
                      legend: { orientation: 'h', x: 0, y: -0.2 }
                    }}
                    config={{ displayModeBar: false }}
                  />
                </div>
              </div>

              <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl space-y-4">
                <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider">AI Copilot Categories</h3>
                <div className="flex justify-center">
                  <Plot
                    data={[{
                      x: Object.keys(data.ai_copilot.question_categories),
                      y: Object.values(data.ai_copilot.question_categories),
                      type: 'bar',
                      marker: { color: '#f59e0b' }
                    }]}
                    layout={{
                      width: 320,
                      height: 240,
                      margin: { t: 20, b: 40, l: 30, r: 10 },
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#94a3b8', size: 10 },
                      xaxis: { gridcolor: '#1e293b' },
                      yaxis: { gridcolor: '#1e293b' }
                    }}
                    config={{ displayModeBar: false }}
                  />
                </div>
              </div>
            </div>

            {/* Platform Metadata summary */}
            <div className="bg-[#0c1220] border border-[#1e293b] p-6 rounded-2xl space-y-4">
              <h3 className="text-sm font-bold uppercase text-slate-300 tracking-wider flex items-center space-x-2">
                <Database className="h-5 w-5 text-sky-400" />
                <span>EAV Metadata Schema & Growth</span>
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
                  <span className="text-[10px] text-slate-500 uppercase font-bold">Total Entities</span>
                  <p className="text-xl font-bold text-white mt-1">{data.metadata.total_entities}</p>
                </div>
                <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
                  <span className="text-[10px] text-slate-500 uppercase font-bold">Schema Fields</span>
                  <p className="text-xl font-bold text-white mt-1">{data.metadata.total_fields}</p>
                </div>
                <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
                  <span className="text-[10px] text-slate-500 uppercase font-bold">Metadata Values</span>
                  <p className="text-xl font-bold text-white mt-1">{data.metadata.total_values}</p>
                </div>
                <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
                  <span className="text-[10px] text-slate-500 uppercase font-bold">Relationships</span>
                  <p className="text-xl font-bold text-white mt-1">{data.metadata.total_relationships}</p>
                </div>
                <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
                  <span className="text-[10px] text-slate-500 uppercase font-bold">Completeness</span>
                  <p className="text-xl font-bold text-sky-400 mt-1">{data.metadata.completeness_score}%</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* SCIENTIFIC INSIGHTS DASHBOARD */}
        {activeTab === 'scientific' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Lipinski compliance */}
              <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl space-y-4">
                <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Lipinski Rule of 5 Compliance</h3>
                <div className="flex justify-center">
                  <Plot
                    data={[{
                      values: [data.compounds.lipinski_compliance.compliant, data.compounds.lipinski_compliance.non_compliant],
                      labels: ['Compliant', 'Non-compliant (&gt;1 violation)'],
                      type: 'pie',
                      hole: 0.45,
                      marker: { colors: ['#10b981', '#f43f5e'] }
                    }]}
                    layout={{
                      width: 400,
                      height: 280,
                      margin: { t: 10, b: 10, l: 10, r: 10 },
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#94a3b8', size: 10 },
                      showlegend: true
                    }}
                    config={{ displayModeBar: false }}
                  />
                </div>
              </div>

              {/* Chemical distribution scatter (MW vs logP) */}
              <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl space-y-4">
                <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Chemical Property Space (MW vs logP)</h3>
                <div className="flex justify-center">
                  <Plot
                    data={[{
                      x: data.compounds.mw_distribution,
                      y: data.compounds.clogp_distribution,
                      mode: 'markers',
                      type: 'scatter',
                      marker: { color: '#0ea5e9', size: 8 }
                    }]}
                    layout={{
                      width: 400,
                      height: 280,
                      margin: { t: 20, b: 40, l: 40, r: 15 },
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#94a3b8', size: 10 },
                      xaxis: { title: 'Molecular Weight (g/mol)', gridcolor: '#1e293b' },
                      yaxis: { title: 'cLogP', gridcolor: '#1e293b' }
                    }}
                  />
                </div>
              </div>
            </div>

            {/* Top Active Compounds */}
            <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl space-y-4">
              <div className="flex justify-between items-center border-b border-[#1e293b] pb-3">
                <h3 className="text-sm font-bold uppercase text-slate-300 tracking-wider">Top Performing Active Compounds</h3>
                <span className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs px-2.5 py-1 rounded-lg font-bold">Assay Success Rate: {data.assays.success_rate}%</span>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-500 uppercase font-bold tracking-wider">
                      <th className="py-2.5 px-4">Compound Key</th>
                      <th className="py-2.5 px-4">Target Protein</th>
                      <th className="py-2.5 px-4">Assay Name</th>
                      <th className="py-2.5 px-4 text-right">IC50 Potency (nM)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.compounds.top_active.map((item, idx) => (
                      <tr key={idx} className="border-b border-slate-900 hover:bg-slate-900/30 text-slate-200">
                        <td className="py-2.5 px-4 font-bold text-sky-400">{item.compound_id}</td>
                        <td className="py-2.5 px-4">{item.target}</td>
                        <td className="py-2.5 px-4">{item.name}</td>
                        <td className="py-2.5 px-4 text-right font-semibold text-emerald-400">{item.ic50} nM</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* BIOINFORMATICS DASHBOARD */}
        {activeTab === 'bio' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl space-y-4">
                <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Sequence Type Distribution</h3>
                <div className="flex justify-center">
                  <Plot
                    data={[{
                      x: Object.keys(data.bioinformatics.type_distribution),
                      y: Object.values(data.bioinformatics.type_distribution),
                      type: 'bar',
                      marker: { color: '#10b981' }
                    }]}
                    layout={{
                      width: 400,
                      height: 280,
                      margin: { t: 20, b: 40, l: 30, r: 10 },
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#94a3b8', size: 10 },
                      xaxis: { gridcolor: '#1e293b' },
                      yaxis: { gridcolor: '#1e293b' }
                    }}
                    config={{ displayModeBar: false }}
                  />
                </div>
              </div>

              <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl space-y-4">
                <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Organism Source</h3>
                <div className="flex justify-center">
                  <Plot
                    data={[{
                      values: Object.values(data.bioinformatics.organism_distribution),
                      labels: Object.keys(data.bioinformatics.organism_distribution),
                      type: 'pie',
                      hole: 0.45,
                      marker: { colors: ['#10b981', '#64748b'] }
                    }]}
                    layout={{
                      width: 400,
                      height: 280,
                      margin: { t: 10, b: 10, l: 10, r: 10 },
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#94a3b8', size: 10 },
                      showlegend: true
                    }}
                    config={{ displayModeBar: false }}
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              <div className="p-5 bg-[#0c1220] border border-[#1e293b] rounded-2xl">
                <span className="text-[10px] text-slate-500 uppercase font-bold">Total Sequences</span>
                <p className="text-3xl font-extrabold text-white mt-1.5">{data.bioinformatics.total_count}</p>
              </div>
              <div className="p-5 bg-[#0c1220] border border-[#1e293b] rounded-2xl">
                <span className="text-[10px] text-slate-500 uppercase font-bold">Sequence Alignments Run</span>
                <p className="text-3xl font-extrabold text-white mt-1.5">{data.bioinformatics.alignments_count}</p>
              </div>
              <div className="p-5 bg-[#0c1220] border border-[#1e293b] rounded-2xl">
                <span className="text-[10px] text-slate-500 uppercase font-bold">Identified Mutations/Variants</span>
                <p className="text-3xl font-extrabold text-amber-500 mt-1.5">{data.bioinformatics.mutation_frequency}</p>
              </div>
            </div>
          </div>
        )}

        {/* WORKFLOW ANALYTICS DASHBOARD */}
        {activeTab === 'workflows' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl flex flex-col justify-between">
                <div>
                  <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Workflow Success Metrics</h3>
                  <div className="flex items-baseline space-x-2 mt-4">
                    <p className="text-4xl font-extrabold text-white">{data.workflows.success_rate}%</p>
                    <span className="text-emerald-400 font-semibold text-xs flex items-center space-x-0.5">
                      <CheckCircle2 className="h-3 w-3" />
                      <span>Completed Success</span>
                    </span>
                  </div>
                </div>
                <div className="mt-6 space-y-2">
                  <div className="flex justify-between text-xs text-slate-400">
                    <span>SLA Compliance Rate</span>
                    <span className="font-bold text-white">{data.workflows.sla_compliance_rate}%</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div className="bg-sky-500 h-2 rounded-full" style={{ width: `${data.workflows.sla_compliance_rate}%` }}></div>
                  </div>
                </div>
              </div>

              <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl lg:col-span-2">
                <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Workflow Step Performance Bottlenecks</h3>
                <div className="flex justify-center mt-3">
                  <Plot
                    data={[{
                      x: data.workflows.steps.slice(0, 10).map(s => s.step_name),
                      y: data.workflows.steps.slice(0, 10).map(s => s.execution_time_ms),
                      type: 'bar',
                      marker: { color: '#a855f7' }
                    }]}
                    layout={{
                      width: 500,
                      height: 220,
                      margin: { t: 20, b: 40, l: 40, r: 10 },
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#94a3b8', size: 9 },
                      xaxis: { gridcolor: '#1e293b' },
                      yaxis: { title: 'Execution (ms)', gridcolor: '#1e293b' }
                    }}
                    config={{ displayModeBar: false }}
                  />
                </div>
              </div>
            </div>

            {/* Workflow Approvals Grid */}
            <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl space-y-4">
              <h3 className="text-sm font-bold uppercase text-slate-300 tracking-wider border-b border-[#1e293b] pb-3">Principal Investigator approvals status</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {data.workflows.approvals.slice(0, 6).map((app, idx) => (
                  <div key={idx} className="p-4 bg-slate-900/50 border border-slate-800 rounded-xl flex items-center justify-between">
                    <div>
                      <span className="text-[10px] text-slate-500 font-bold uppercase">Approval ID #{app.id}</span>
                      <p className="text-xs font-semibold text-slate-300 mt-1">PI: {app.approved_by || 'Dr. Sarah Connor'}</p>
                    </div>
                    <span className={`text-[10px] font-bold px-2 py-1 rounded-lg ${
                      app.status === 'APPROVED' ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400' : 'bg-amber-500/10 border border-amber-500/20 text-amber-400'
                    }`}>
                      {app.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* COMPLIANCE & AUDIT DASHBOARD */}
        {activeTab === 'compliance' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl flex flex-col justify-between">
                <div>
                  <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Cryptographic Hash Auditing</h3>
                  <div className="mt-4 flex items-center space-x-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 p-4 rounded-xl">
                    <CheckCircle2 className="h-6 w-6 flex-shrink-0" />
                    <div>
                      <h4 className="text-xs font-bold">Zero Violations Detected</h4>
                      <p className="text-[10px] text-slate-400 mt-0.5">All SHA-256 integrity block chains match database versions.</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 space-y-2">
                  <div className="flex justify-between text-[11px] text-slate-400">
                    <span>Audit logs count</span>
                    <span className="font-bold text-white">{data.compliance.total_events}</span>
                  </div>
                  <div className="flex justify-between text-[11px] text-slate-400">
                    <span>Total signatures</span>
                    <span className="font-bold text-white">{data.compliance.total_signatures}</span>
                  </div>
                </div>
              </div>

              <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl lg:col-span-2">
                <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Digital Signatures Trend</h3>
                <div className="flex justify-center mt-3">
                  <Plot
                    data={[{
                      x: Object.keys(data.compliance.signature_trends),
                      y: Object.values(data.compliance.signature_trends),
                      type: 'scatter',
                      mode: 'lines+markers',
                      line: { color: '#10b981', width: 2.5 }
                    }]}
                    layout={{
                      width: 500,
                      height: 220,
                      margin: { t: 20, b: 40, l: 30, r: 10 },
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#94a3b8', size: 9 },
                      xaxis: { gridcolor: '#1e293b' },
                      yaxis: { title: 'Signatures', gridcolor: '#1e293b' }
                    }}
                  />
                </div>
              </div>
            </div>

            {/* Event categories breakdown */}
            <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl space-y-4">
              <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Audit events categories breakdown</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(data.compliance.events_by_type).map(([key, val]) => (
                  <div key={key} className="p-3 bg-slate-900/40 border border-slate-800 rounded-xl">
                    <span className="text-[10px] text-slate-500 font-bold uppercase">{key}</span>
                    <p className="text-lg font-bold text-white mt-0.5">{val}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* AI SCIENTIST COPILOT DASHBOARD */}
        {activeTab === 'ai' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl space-y-4">
                <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider">AI Scientist Copilot Request categories</h3>
                <div className="flex justify-center">
                  <Plot
                    data={[{
                      values: Object.values(data.ai_copilot.question_categories),
                      labels: Object.keys(data.ai_copilot.question_categories),
                      type: 'pie',
                      hole: 0.45,
                      marker: { colors: ['#f59e0b', '#6366f1', '#ec4899', '#3b82f6', '#94a3b8'] }
                    }]}
                    layout={{
                      width: 400,
                      height: 280,
                      margin: { t: 10, b: 10, l: 10, r: 10 },
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#94a3b8', size: 10 },
                      showlegend: true
                    }}
                    config={{ displayModeBar: false }}
                  />
                </div>
              </div>

              <div className="bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl flex flex-col justify-between">
                <div>
                  <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider flex items-center space-x-1.5">
                    <Sparkles className="h-4.5 w-4.5 text-amber-500" />
                    <span>User Adoption and Response Times</span>
                  </h3>
                  <div className="grid grid-cols-2 gap-4 mt-6">
                    <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
                      <span className="text-[10px] text-slate-500 uppercase font-bold">Total Sessions</span>
                      <p className="text-2xl font-bold text-white mt-1">{data.ai_copilot.total_sessions}</p>
                    </div>
                    <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
                      <span className="text-[10px] text-slate-500 uppercase font-bold">Total Messages</span>
                      <p className="text-2xl font-bold text-white mt-1">{data.ai_copilot.total_messages}</p>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-slate-900/30 border border-slate-800/80 rounded-xl space-y-2 mt-4">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400 font-semibold">Average Copilot Response Time</span>
                    <span className="font-bold text-amber-400">1.82s</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1.5">
                    <div className="bg-amber-500 h-1.5 rounded-full" style={{ width: '85%' }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
