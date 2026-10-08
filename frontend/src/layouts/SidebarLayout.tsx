import { useState } from 'react';
import { Link, useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import {
  LayoutDashboard,
  Database,
  LogOut,
  User,
  Search,
  ShieldCheck,
  Plug,
  FlaskConical,
  GitMerge,
  BarChart4,
  Dna,
  Sparkles,
  BookOpen,
  Activity,
  CircleHelp,
  ChevronRight,
  BrainCircuit,
} from 'lucide-react';
import { UserGuideModal } from '../components/UserGuideModal';

export const SidebarLayout = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [isUserGuideOpen, setIsUserGuideOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Overview', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Clinical Metadata', path: '/metadata', icon: Database },
    { name: 'Query Builder', path: '/query-builder', icon: Search },
    { name: 'Workflow Designer', path: '/workflows', icon: GitMerge },
    { name: 'AI Scientist Copilot', path: '/copilot', icon: Sparkles },
    { name: 'Analytics Dashboard', path: '/analytics-dashboard', icon: BarChart4 },
    { name: 'Analytics Workbench', path: '/analytics-workbench', icon: Activity },
    { name: 'Compound Explorer', path: '/compounds', icon: FlaskConical },
    { name: 'SAR Decomposition', path: '/sar', icon: GitMerge },
    { name: 'Bioinformatics Hub', path: '/bioinformatics', icon: Dna },
    { name: 'Data Connectors', path: '/connectors', icon: Plug },
    { name: 'Enterprise Integrations', path: '/connectors/enterprise', icon: Plug },
    { name: 'Compliance Console', path: '/compliance', icon: ShieldCheck },
    { name: 'Audit Trail', path: '/admin/audit', icon: ShieldCheck },
  ];

  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/dashboard') return 'Clinical Intelligence Overview';
    if (path === '/metadata') return 'Clinical Metadata Catalog';
    if (path === '/query-builder') return 'Visual Query Builder';
    if (path === '/workflows') return 'Scientific Workflow Designer';
    if (path === '/copilot') return 'AI Scientist Copilot';
    if (path === '/analytics-dashboard') return 'Clinical Analytics Dashboard';
    if (path === '/analytics-workbench') return 'Scientific Analytics Workbench';
    if (path === '/compounds') return 'Compound Explorer';
    if (path === '/sar') return 'SAR Decomposition';
    if (path === '/connectors/enterprise') return 'Enterprise Integrations Hub';
    if (path.startsWith('/connectors')) return 'Data Connector Hub';
    if (path === '/admin/audit') return 'Audit Trail & Compliance';
    if (path === '/compliance') return 'Compliance Console';
    if (path === '/bioinformatics') return 'Bioinformatics Hub';
    if (path === '/sequences') return 'Sequence Explorer';
    if (path === '/alignments') return 'Sequence Alignment Studio';
    if (path === '/clusters') return 'Sequence Clustering Center';
    if (path === '/user-guide') return 'Clinical AI Observatory Guide';
    return 'Clinical AI Observatory';
  };

  return (
    <div className="cao-shell-grid flex h-screen bg-[#07111f] text-slate-100 overflow-hidden">
      <aside className="w-[272px] bg-[#091525]/95 flex flex-col border-r border-slate-800/80 h-full flex-shrink-0">
        <div className="px-5 py-5 border-b border-slate-800/80">
          <Link to="/dashboard" className="flex items-center gap-3 group">
            <div className="cao-brand-mark h-11 w-11 rounded-2xl border border-cyan-400/25 bg-cyan-400/10 flex items-center justify-center text-cyan-300 transition-transform group-hover:scale-[1.03]">
              <BrainCircuit className="h-6 w-6" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <h1 className="font-bold text-[16px] tracking-tight text-white truncate">Clinical AI</h1>
                <span className="text-[9px] px-1.5 py-0.5 rounded-full border border-teal-400/20 bg-teal-400/10 text-teal-300 font-bold">AI</span>
              </div>
              <p className="text-[10px] text-slate-400 font-semibold uppercase tracking-[0.16em] mt-0.5">Observatory</p>
            </div>
          </Link>
        </div>

        <div className="px-3 pt-4 pb-2">
          <p className="px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">Platform</p>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 pb-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.name}
                to={item.path}
                className={[
                  'group flex items-center justify-between gap-3 px-3.5 py-2.5 rounded-xl text-[13px] font-medium transition-all border',
                  isActive
                    ? 'bg-cyan-400/10 text-cyan-200 border-cyan-400/20 shadow-[0_0_24px_rgba(56,189,248,0.07)]'
                    : 'text-slate-400 hover:bg-white/[0.035] hover:text-slate-100 border-transparent',
                ].join(' ')}
              >
                <span className="flex items-center gap-3 min-w-0">
                  <Icon className={`h-[17px] w-[17px] shrink-0 ${isActive ? 'text-cyan-300' : 'text-slate-500 group-hover:text-slate-300'}`} />
                  <span className="truncate">{item.name}</span>
                </span>
                {isActive && <ChevronRight className="h-3.5 w-3.5 text-cyan-300/70 shrink-0" />}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-800/80 bg-[#081221]">
          <div className="rounded-2xl border border-slate-800/90 bg-white/[0.025] p-3.5">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-xl bg-slate-800 flex items-center justify-center text-slate-300 border border-slate-700/80">
                <User className="h-4 w-4" />
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold text-white truncate">{user?.email}</p>
                <p className="text-[10px] text-cyan-300 font-semibold mt-0.5">{user?.role}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="mt-3 flex items-center gap-2 text-xs text-slate-400 hover:text-rose-300 font-semibold px-2.5 py-2 hover:bg-rose-500/5 rounded-lg w-full transition-colors"
            >
              <LogOut className="h-3.5 w-3.5" />
              <span>Sign out</span>
            </button>
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-[74px] bg-[#081525]/90 backdrop-blur-xl border-b border-slate-800/80 px-7 flex items-center justify-between shrink-0">
          <div>
            <p className="text-[10px] uppercase tracking-[0.18em] text-cyan-300/70 font-bold">Clinical AI Observatory</p>
            <h2 className="font-semibold text-[18px] text-white tracking-tight mt-0.5">{getPageTitle()}</h2>
          </div>

          <div className="flex items-center gap-2.5">
            <Link
              to="/metadata"
              className="hidden sm:flex items-center gap-2 bg-white/[0.035] hover:bg-white/[0.06] text-slate-200 px-3.5 py-2 rounded-xl text-xs font-semibold transition-colors border border-slate-800"
            >
              <Database className="h-3.5 w-3.5 text-cyan-300" />
              Data Registry
            </Link>

            <button
              onClick={() => setIsUserGuideOpen(true)}
              className="hidden md:flex items-center gap-2 bg-white/[0.035] hover:bg-white/[0.06] text-slate-200 px-3.5 py-2 rounded-xl text-xs font-semibold transition-colors border border-slate-800"
            >
              <BookOpen className="h-3.5 w-3.5 text-teal-300" />
              Guide
            </button>

            <div className="hidden lg:flex items-center gap-2 px-3 py-2 rounded-xl border border-emerald-400/15 bg-emerald-400/[0.04] text-[10px] font-bold tracking-[0.12em] text-emerald-300">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-300 animate-pulse" />
              SECURE
            </div>

            <div className="flex items-center gap-2 bg-slate-900/75 border border-slate-800 text-slate-200 px-3.5 py-2 rounded-xl text-xs font-semibold">
              <CircleHelp className="h-3.5 w-3.5 text-slate-400" />
              <span className="max-w-[120px] truncate">{user?.email ? user.email.split('@')[0] : 'researcher'}</span>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-5 sm:p-7 bg-transparent">
          <Outlet />
        </main>
      </div>

      <UserGuideModal isOpen={isUserGuideOpen} onClose={() => setIsUserGuideOpen(false)} />
    </div>
  );
};
