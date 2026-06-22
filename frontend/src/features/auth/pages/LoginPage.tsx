import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../../store/useAuthStore';
import { apiRequest } from '../../../services/api';
import { Award, Lock, Mail, User, ShieldCheck, AlertCircle } from 'lucide-react';

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
        // Handle Register
        await apiRequest('/auth/register', {
          method: 'POST',
          service: 'auth',
          body: JSON.stringify({ email, password, full_name: fullName, role }),
        });
        setSuccess('Account created successfully! Please sign in.');
        setIsRegister(false);
        setPassword('');
      } else {
        // Handle Login
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
    <div className="min-h-screen bg-[#070b13] flex flex-col justify-center items-center p-4 relative overflow-hidden">
      {/* Background gradients */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-sky-500/10 rounded-full blur-[120px]"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-teal-500/10 rounded-full blur-[120px]"></div>

      <div className="w-full max-w-md glass-panel p-8 rounded-2xl border border-slate-800 shadow-[0_20px_50px_rgba(0,0,0,0.5)] z-10">
        {/* Brand */}
        <div className="flex flex-col items-center mb-8">
          <div className="bg-sky-500/25 p-3 rounded-2xl border border-sky-500/40 mb-3 shadow-[0_0_20px_rgba(14,165,233,0.2)]">
            <Award className="h-8 w-8 text-sky-400" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-wider">GENQUANTAA DISCOVER</h1>
          <p className="text-xs text-slate-400 mt-1 uppercase tracking-widest">Scientific Informatics Platform</p>
        </div>

        {/* Success/Error Alerts */}
        {error && (
          <div className="flex items-center space-x-2 bg-rose-500/10 border border-rose-500/20 text-rose-400 p-3 rounded-lg text-sm mb-4">
            <AlertCircle className="h-5 w-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
        {success && (
          <div className="flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 p-3 rounded-lg text-sm mb-4">
            <ShieldCheck className="h-5 w-5 flex-shrink-0" />
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <>
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-5 w-5 text-slate-500" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Dr. Sarah Jenkins"
                    className="w-full bg-[#0d1322] border border-slate-800 focus:border-sky-500 rounded-lg py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Role Type</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full bg-[#0d1322] border border-slate-800 focus:border-sky-500 rounded-lg py-2.5 px-4 text-sm text-slate-100 focus:outline-none transition-all"
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
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 h-5 w-5 text-slate-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="scientist@company.com"
                className="w-full bg-[#0d1322] border border-slate-800 focus:border-sky-500 rounded-lg py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-5 w-5 text-slate-500" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-[#0d1322] border border-slate-800 focus:border-sky-500 rounded-lg py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-600 hover:to-teal-600 text-white rounded-lg py-2.5 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-sky-500/50 transition-all shadow-[0_4px_20px_rgba(14,165,233,0.3)] disabled:opacity-50 cursor-pointer"
          >
            {loading ? 'Processing...' : isRegister ? 'Create Account' : 'Sign In'}
          </button>
        </form>

        {/* Toggle Mode */}
        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsRegister(!isRegister);
              setError(null);
            }}
            className="text-xs text-sky-400 hover:text-sky-300 font-medium transition-colors focus:outline-none cursor-pointer"
          >
            {isRegister ? 'Already have an account? Sign In' : "Don't have an account? Register"}
          </button>
        </div>
      </div>
    </div>
  );
};
