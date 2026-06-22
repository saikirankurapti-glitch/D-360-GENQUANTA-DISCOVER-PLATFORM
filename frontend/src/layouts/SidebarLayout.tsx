import { Link, useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { LayoutDashboard, Database, LogOut, User, Search, Award, Plug, FlaskConical, GitMerge, BarChart4, ShieldCheck, Dna, Sparkles } from 'lucide-react';

export const SidebarLayout = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Metadata Catalog', path: '/metadata', icon: Database },
    { name: 'Query Builder', path: '/query-builder', icon: Search },
    { name: 'Workflow Designer', path: '/workflows', icon: GitMerge },
    { name: 'AI Scientist Copilot', path: '/copilot', icon: Sparkles },
    { name: 'Analytics Workbench', path: '/analytics-workbench', icon: BarChart4 },
    { name: 'Compound Explorer', path: '/compounds', icon: FlaskConical },
    { name: 'SAR Decomposition', path: '/sar', icon: GitMerge },
    { name: 'Data Connectors', path: '/connectors', icon: Plug },
    { name: 'Enterprise Integrations', path: '/connectors/enterprise', icon: Plug },
    { name: 'Audit Trail', path: '/admin/audit', icon: ShieldCheck },
    { name: 'Compliance Console', path: '/compliance', icon: ShieldCheck },
    { name: 'Bioinformatics Hub', path: '/bioinformatics', icon: Dna },
  ];

  return (
    <div className="flex h-screen bg-[#070b13] text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-[#0c1220] flex flex-col justify-between border-r border-[#1e293b]">
        <div>
          {/* Logo */}
          <div className="p-6 border-b border-[#1e293b] flex items-center space-x-3">
            <div className="bg-sky-500/20 p-2 rounded-lg border border-sky-500/40">
              <Award className="h-6 w-6 text-sky-400" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-wider text-white">GENQUANTAA</h1>
              <p className="text-[10px] text-sky-400 font-semibold uppercase tracking-widest">Discover Platform</p>
            </div>
          </div>

          {/* Nav Links */}
          <nav className="p-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-sky-500/10 text-sky-400 border border-sky-500/25 shadow-[0_0_15px_rgba(14,165,233,0.1)]'
                      : 'text-slate-400 hover:bg-[#131b2e] hover:text-slate-200 border border-transparent'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* User profile footer */}
        <div className="p-4 border-t border-[#1e293b] space-y-3 bg-[#0a0f1b]">
          <div className="flex items-center space-x-3">
            <div className="bg-[#1e293b] p-2 rounded-full text-slate-300">
              <User className="h-5 w-5" />
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-semibold text-white truncate">{user?.email}</p>
              <p className="text-[10px] text-sky-400 font-medium">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center space-x-2 text-xs text-rose-400 hover:text-rose-300 font-semibold px-4 py-2 hover:bg-rose-500/5 rounded-lg w-full transition-all"
          >
            <LogOut className="h-4 w-4" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-[#0c1220] border-b border-[#1e293b] px-8 flex items-center justify-between">
          <h2 className="font-semibold text-lg text-slate-200">
            {location.pathname === '/dashboard'
              ? 'Informatics Hub'
              : location.pathname === '/query-builder'
              ? 'Visual Query Builder'
              : location.pathname === '/workflows'
              ? 'Scientific Workflow Designer'
              : location.pathname === '/analytics-workbench'
              ? 'Scientific Analytics Workbench'
              : location.pathname === '/compounds'
              ? 'Compound Explorer'
              : location.pathname === '/sar'
              ? 'SAR Decomposition'
              : location.pathname === '/connectors/enterprise'
              ? 'Enterprise Integrations Hub'
              : location.pathname.startsWith('/connectors')
              ? 'Data Connector Hub'
              : location.pathname === '/admin/audit'
              ? 'Audit Trail & Compliance Logs'
              : location.pathname === '/compliance'
              ? 'Compliance Console'
              : location.pathname === '/bioinformatics'
              ? 'Bioinformatics Hub'
              : location.pathname === '/sequences'
              ? 'Sequence Explorer'
              : location.pathname === '/alignments'
              ? 'Sequence Alignment Studio'
              : location.pathname === '/clusters'
              ? 'Sequence Clustering Center'
              : 'Metadata Catalog'}
          </h2>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full">
              <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
              <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider">Services Online</span>
            </div>
            <span className="text-xs text-slate-400">June 16, 2026</span>
          </div>
        </header>

        {/* Page body */}
        <main className="flex-1 overflow-y-auto p-8 bg-[#070b13] flex flex-col">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
