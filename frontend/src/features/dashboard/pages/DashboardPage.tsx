import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../../../services/api';
import { Database, ShieldCheck, Microscope, FlaskConical, TrendingDown, RefreshCw } from 'lucide-react';

export const DashboardPage = () => {
  const [stats, setStats] = useState({
    compounds: 0,
    assays: 0,
    fields: 0,
  });
  const [loading, setLoading] = useState(true);
  const [isBootstrapped, setIsBootstrapped] = useState(false);
  const navigate = useNavigate();

  const fetchStats = async () => {
    try {
      setLoading(true);
      const entities = await apiRequest('/metadata/entities');
      const fields = await apiRequest('/metadata/fields');

      const compounds = entities.filter((e: any) => e.entity_type === 'Compound').length;
      const assays = entities.filter((e: any) => e.entity_type === 'Assay').length;

      setStats({
        compounds,
        assays,
        fields: fields.length,
      });

      if (entities.length > 0) {
        setIsBootstrapped(true);
      }
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBootstrap = async () => {
    try {
      setLoading(true);
      await apiRequest('/metadata/bootstrap', { method: 'POST' });
      await fetchStats();
    } catch (error) {
      console.error('Bootstrap failed:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="space-y-8">
      {/* Bootstrap Banner if Database is Empty */}
      {!loading && !isBootstrapped && (
        <div className="bg-gradient-to-r from-sky-500/10 to-teal-500/10 border border-sky-500/30 p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h3 className="text-lg font-bold text-white">Database is unseeded</h3>
            <p className="text-sm text-slate-400">Initialize the metadata catalog with demo assay data and chemical compound records.</p>
          </div>
          <button
            onClick={handleBootstrap}
            className="flex items-center space-x-2 bg-sky-500 hover:bg-sky-600 text-white px-5 py-2.5 rounded-xl text-sm font-semibold shadow-[0_4px_15px_rgba(14,165,233,0.3)] transition-all cursor-pointer"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Seed Database</span>
          </button>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Chemical Entities</p>
            <h3 className="text-3xl font-extrabold text-white">{loading ? '...' : stats.compounds}</h3>
            <p className="text-[10px] text-emerald-400 flex items-center">
              <TrendingDown className="h-3.5 w-3.5 mr-1" />
              <span>SMILES Rendered</span>
            </p>
          </div>
          <div className="bg-sky-500/10 border border-sky-500/20 p-4 rounded-xl text-sky-400">
            <FlaskConical className="h-6 w-6" />
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">BioAssays Registered</p>
            <h3 className="text-3xl font-extrabold text-white">{loading ? '...' : stats.assays}</h3>
            <p className="text-[10px] text-sky-400 flex items-center">
              <ShieldCheck className="h-3.5 w-3.5 mr-1" />
              <span>IC50 Ranges Calibrated</span>
            </p>
          </div>
          <div className="bg-teal-500/10 border border-teal-500/20 p-4 rounded-xl text-teal-400">
            <Microscope className="h-6 w-6" />
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Catalog Schema Fields</p>
            <h3 className="text-3xl font-extrabold text-white">{loading ? '...' : stats.fields}</h3>
            <p className="text-[10px] text-teal-400 flex items-center">
              <Database className="h-3.5 w-3.5 mr-1" />
              <span>Flexible EAV Mapping</span>
            </p>
          </div>
          <div className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-xl text-emerald-400">
            <Database className="h-6 w-6" />
          </div>
        </div>
      </div>

      {/* Main Grid section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Dynamic Plot */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 lg:col-span-2 space-y-6">
          <div className="flex justify-between items-center border-b border-slate-800 pb-4">
            <div>
              <h4 className="font-bold text-white">IC50 Compound Inhibition Profile</h4>
              <p className="text-xs text-slate-400">Comparing IC50 concentration profile across EGFR assays (in nM)</p>
            </div>
            <span className="text-[10px] bg-sky-500/15 text-sky-400 border border-sky-500/30 px-2 py-0.5 rounded font-bold uppercase">Active Chart</span>
          </div>

          {/* SVG Chart */}
          <div className="h-64 flex justify-center items-center bg-[#0a0f1b] rounded-xl relative p-4">
            {stats.compounds === 0 ? (
              <p className="text-sm text-slate-500">Seed the database to visualize assay values</p>
            ) : (
              <svg className="w-full h-full" viewBox="0 0 500 220">
                {/* Grid Lines */}
                <line x1="50" y1="20" x2="480" y2="20" stroke="#1e293b" strokeDasharray="4" />
                <line x1="50" y1="70" x2="480" y2="70" stroke="#1e293b" strokeDasharray="4" />
                <line x1="50" y1="120" x2="480" y2="120" stroke="#1e293b" strokeDasharray="4" />
                <line x1="50" y1="170" x2="480" y2="170" stroke="#1e293b" strokeDasharray="4" />
                <line x1="50" y1="170" x2="480" y2="170" stroke="#334155" />

                {/* Y Axis Labels */}
                <text x="15" y="25" fill="#64748b" className="text-[10px] font-bold">15.0 nM</text>
                <text x="15" y="75" fill="#64748b" className="text-[10px] font-bold">10.0 nM</text>
                <text x="15" y="125" fill="#64748b" className="text-[10px] font-bold">5.0 nM</text>
                <text x="15" y="175" fill="#64748b" className="text-[10px] font-bold">0.0 nM</text>

                {/* Compound bars */}
                {/* CMP-001 (IC50: 3.2nM -> height roughly 3.2/15 * 150 = 32px. y coordinate: 170 - 32 = 138) */}
                <rect x="90" y="138" width="45" height="32" fill="url(#sky-gradient)" rx="4" />
                <text x="95" y="130" fill="#38bdf8" className="text-[10px] font-bold">3.2 nM</text>
                <text x="95" y="192" fill="#94a3b8" className="text-[10px] font-medium">CMP-001</text>

                {/* CMP-002 (IC50: 12.5nM -> height roughly 12.5/15 * 150 = 125px. y coordinate: 170 - 125 = 45) */}
                <rect x="180" y="45" width="45" height="125" fill="url(#sky-gradient)" rx="4" />
                <text x="185" y="37" fill="#38bdf8" className="text-[10px] font-bold">12.5 nM</text>
                <text x="185" y="192" fill="#94a3b8" className="text-[10px] font-medium">CMP-002</text>

                {/* CMP-003 (IC50: 0.8nM -> height roughly 8px. y coordinate: 162) */}
                <rect x="270" y="162" width="45" height="8" fill="url(#teal-gradient)" rx="4" />
                <text x="275" y="154" fill="#2dd4bf" className="text-[10px] font-bold">0.8 nM</text>
                <text x="275" y="192" fill="#94a3b8" className="text-[10px] font-medium">CMP-003</text>

                {/* CMP-004 (IC50: 9.1nM -> height roughly 91px. y coordinate: 79) */}
                <rect x="360" y="79" width="45" height="91" fill="url(#sky-gradient)" rx="4" />
                <text x="365" y="71" fill="#38bdf8" className="text-[10px] font-bold">9.1 nM</text>
                <text x="365" y="192" fill="#94a3b8" className="text-[10px] font-medium">CMP-004</text>

                {/* Gradients */}
                <defs>
                  <linearGradient id="sky-gradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#0ea5e9" />
                    <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0.2" />
                  </linearGradient>
                  <linearGradient id="teal-gradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#14b8a6" />
                    <stop offset="100%" stopColor="#14b8a6" stopOpacity="0.2" />
                  </linearGradient>
                </defs>
              </svg>
            )}
          </div>
        </div>

        {/* Quick Actions Panel */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
          <h4 className="font-bold text-white border-b border-slate-800 pb-4">Discovery Actions</h4>
          
          <div className="space-y-4">
            <button
              onClick={() => navigate('/metadata')}
              className="w-full flex items-center justify-between p-4 bg-[#0d1322] border border-slate-800 hover:border-sky-500/40 rounded-xl transition-all cursor-pointer group text-left"
            >
              <div>
                <p className="text-sm font-semibold text-white group-hover:text-sky-400">Search Metadata</p>
                <p className="text-xs text-slate-400 mt-1">Browse, filter, and inspect structural descriptors.</p>
              </div>
              <Database className="h-5 w-5 text-slate-500 group-hover:text-sky-400" />
            </button>

            <div className="p-4 bg-[#0a0f1b] border border-slate-900 rounded-xl opacity-60">
              <p className="text-sm font-semibold text-slate-500">Visual Query Builder</p>
              <p className="text-xs text-slate-600 mt-1">Design complex multi-assay joins visually.</p>
              <span className="inline-block text-[9px] bg-slate-800 text-slate-400 font-bold px-1.5 py-0.5 rounded mt-2 uppercase tracking-wide">Phase 2</span>
            </div>

            <div className="p-4 bg-[#0a0f1b] border border-slate-900 rounded-xl opacity-60">
              <p className="text-sm font-semibold text-slate-500">Compound Similarity</p>
              <p className="text-xs text-slate-600 mt-1">Substructure and Morgan fingerprint search.</p>
              <span className="inline-block text-[9px] bg-slate-800 text-slate-400 font-bold px-1.5 py-0.5 rounded mt-2 uppercase tracking-wide">Phase 2</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
