import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../../store/useAuthStore';
import { apiRequest } from '../../../services/api';
import { Lock, Mail, User, ShieldCheck, AlertCircle, BrainCircuit, Sparkles } from 'lucide-react';

export const LoginPage = () => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('Scientist');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);

  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      if (isRegister) {
        await apiRequest('/auth/register', {
          method: 'POST',
          service: 'auth',
          body: JSON.stringify({ email, password, full_name: fullName, role }),
        });
        setSuccess('Account created successfully. Please sign in.');
        setIsRegister(false);
        setPassword('');
      } else {
        const data = await apiRequest('/auth/login', {
          method: 'POST',
          service: 'auth',
          body: JSON.stringify({ email, password }),
        });
        login(data.access_token, data.refresh_token, data.role, email);
        navigate('/dashboard');
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check your inputs.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cao-shell-grid min-h-screen bg-[#07111f] text-slate-100 flex items-center justify-center p-5 relative overflow-hidden">
      <div className="absolute -top-32 -left-24 w-80 h-80 rounded-full bg-cyan-400/10 blur-3xl" />
      <div className="absolute -bottom-40 -right-28 w-[28rem] h-[28rem] rounded-full bg-teal-400/10 blur-3xl" />

      <div className="w-full max-w-5xl grid lg:grid-cols-[1.1fr_0.9fr] overflow-hidden rounded-[28px] border border-slate-800/80 bg-[#091525]/90 shadow-[0_35px_90px_rgba(0,0,0,0.38)] backdrop-blur-xl relative z-10">
        <div className="hidden lg:flex flex-col justify-between p-10 border-r border-slate-800/80 bg-gradient-to-br from-cyan-400/[0.06] via-transparent to-teal-400/[0.05]">
          <div>
            <div className="flex items-center gap-3">
              <div className="cao-brand-mark h-12 w-12 rounded-2xl border border-cyan-300/25 bg-cyan-300/10 flex items-center justify-center">
                <BrainCircuit className="h-6 w-6 text-cyan-300" />
              </div>
              <div>
                <p className="text-[17px] font-bold text-white">Clinical AI Observatory</p>
                <p className="text-[10px] tracking-[0.18em] uppercase text-slate-500 mt-0.5">Clinical intelligence platform</p>
              </div>
            </div>

            <div className="mt-20 max-w-lg">
              <div className="inline-flex items-center gap-2 rounded-full border border-cyan-300/15 bg-cyan-300/[0.05] px-3 py-1.5 text-[10px] uppercase tracking-[0.16em] font-bold text-cyan-200">
                <Sparkles className="h-3 w-3" />
                Research intelligence
              </div>
              <h2 className="mt-5 text-4xl font-semibold tracking-tight text-white leading-tight">
                One observatory for clinical data, science, and compliant AI.
              </h2>
              <p className="mt-5 text-sm leading-6 text-slate-400 max-w-md">
                Discover structured evidence, connect enterprise data, analyze scientific signals, and orchestrate clinical workflows from one secure workspace.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {[
              ['Metadata', 'Catalog & discovery'],
              ['Analytics', 'Evidence & insight'],
              ['Compliance', 'Audit-ready controls'],
            ].map(([title, subtitle]) => (
              <div key={title} className="rounded-2xl border border-slate-800/90 bg-white/[0.025] p-3.5">
                <p className="text-xs font-semibold text-slate-200">{title}</p>
                <p className="mt-1 text-[10px] leading-4 text-slate-500">{subtitle}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="p-6 sm:p-9">
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="h-11 w-11 rounded-2xl border border-cyan-300/25 bg-cyan-300/10 flex items-center justify-center">
              <BrainCircuit className="h-6 w-6 text-cyan-300" />
            </div>
            <div>
              <h1 className="text-base font-bold text-white">Clinical AI Observatory</h1>
              <p className="text-[9px] uppercase tracking-[0.16em] text-slate-500">Clinical intelligence platform</p>
            </div>
          </div>

          <div className="mb-7">
            <p className="text-[10px] uppercase tracking-[0.18em] font-bold text-cyan-300/70">
              {isRegister ? 'Workspace access' : 'Secure sign in'}
            </p>
            <h1 className="mt-2 text-2xl font-semibold text-white tracking-tight">
              {isRegister ? 'Create your research account' : 'Welcome back'}
            </h1>
            <p className="mt-2 text-sm text-slate-500">
              {isRegister ? 'Provision access to the observatory workspace.' : 'Continue to your clinical intelligence workspace.'}
            </p>
          </div>

          {error && (
            <div className="flex items-start gap-2 bg-rose-500/[0.08] border border-rose-400/15 text-rose-300 p-3 rounded-xl text-xs mb-4">
              <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="flex items-start gap-2 bg-emerald-400/[0.07] border border-emerald-400/15 text-emerald-300 p-3 rounded-xl text-xs mb-4">
              <ShieldCheck className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <span>{success}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <>
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-[0.12em] mb-2">Full Name</label>
                  <div className="relative">
                    <User className="absolute left-3.5 top-3 h-4 w-4 text-slate-600" />
                    <input
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Dr. Sarah Jenkins"
                      className="w-full bg-[#0b1627] border border-slate-800 hover:border-slate-700 focus:border-cyan-400/40 rounded-xl py-3 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-[0.12em] mb-2">Role</label>
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full bg-[#0b1627] border border-slate-800 hover:border-slate-700 focus:border-cyan-400/40 rounded-xl py-3 px-4 text-sm text-slate-100 focus:outline-none transition-all"
                  >
                    <option value="Scientist">Scientist</option>
                    <option value="Project Lead">Project Lead</option>
                    <option value="Administrator">Administrator</option>
                    <option value="External Collaborator">External Collaborator</option>
                  </select>
                </div>
              </>
            )}

            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-[0.12em] mb-2">Email address</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-3 h-4 w-4 text-slate-600" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="scientist@company.com"
                  className="w-full bg-[#0b1627] border border-slate-800 hover:border-slate-700 focus:border-cyan-400/40 rounded-xl py-3 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-[0.12em] mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-3 h-4 w-4 text-slate-600" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-[#0b1627] border border-slate-800 hover:border-slate-700 focus:border-cyan-400/40 rounded-xl py-3 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 bg-gradient-to-r from-cyan-400 to-teal-400 hover:from-cyan-300 hover:to-teal-300 text-[#041018] rounded-xl py-3 text-sm font-bold transition-all shadow-[0_10px_30px_rgba(45,212,191,0.14)] disabled:opacity-50 cursor-pointer"
            >
              {loading ? 'Processing…' : isRegister ? 'Create account' : 'Sign in to Observatory'}
            </button>
          </form>

          <div className="mt-6 pt-5 border-t border-slate-800/70 text-center">
            <button
              onClick={() => {
                setIsRegister(!isRegister);
                setError(null);
                setSuccess(null);
              }}
              className="text-xs font-semibold text-cyan-300 hover:text-cyan-200 transition-colors cursor-pointer"
            >
              {isRegister ? 'Already have an account? Sign in' : "New to the Observatory? Create an account"}
            </button>
          </div>

          <div className="mt-5 flex items-center justify-center gap-2 text-[10px] text-slate-600">
            <ShieldCheck className="h-3.5 w-3.5" />
            Secure clinical workspace
          </div>
        </div>
      </div>
    </div>
  );
};
