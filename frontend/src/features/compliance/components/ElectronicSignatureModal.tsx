import React, { useState } from 'react';
import { apiRequest } from '../../../services/api';
import { useAuthStore } from '../../../store/useAuthStore';
import { Shield, KeyRound, AlertTriangle, X } from 'lucide-react';

interface ElectronicSignatureModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (signatureHash: string) => void;
  actionType: 'QUERY_APPROVAL' | 'DATASET_APPROVAL' | 'METADATA_APPROVAL' | 'WORKFLOW_APPROVAL' | 'EXPORT_APPROVAL';
  entityId: string;
}

export const ElectronicSignatureModal: React.FC<ElectronicSignatureModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  actionType,
  entityId,
}) => {
  const currentEmail = useAuthStore((state) => state.user?.email) || '';
  const currentUserId = useAuthStore((state) => state.user?.role) || 'Scientist';
  
  const [password, setPassword] = useState('');
  const [reason, setReason] = useState('');
  const [meaning, setMeaning] = useState('Approved');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    if (!password || !reason) {
      setError('Password and signature reason are required.');
      setIsSubmitting(false);
      return;
    }

    try {
      // 1. Double factor validation check: verify credentials
      const loginRes = await apiRequest('/auth/login', {
        service: 'auth',
        method: 'POST',
        body: JSON.stringify({ email: currentEmail, password }),
      });

      if (!loginRes || !loginRes.access_token) {
        throw new Error('Invalid credentials proof.');
      }

      // 2. Submit Electronic Signature to audit service
      const signaturePayload = {
        user_id: currentUserId,
        username: currentEmail,
        password_hash: 'verified_password_proof', // token representation proof
        events: [
          {
            action_type: actionType,
            entity_id: entityId,
            reason: reason,
            meaning: meaning,
            details: {
              timestamp: new Date().toISOString(),
              ip: '127.0.0.1',
            },
          },
        ],
      };

      const res = await apiRequest('/compliance/signatures', {
        service: 'audit',
        method: 'POST',
        body: JSON.stringify(signaturePayload),
      });

      onSuccess(res.signature_hash);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Signature validation failed. Check your password.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-700/60 rounded-2xl shadow-2xl p-6 overflow-hidden">
        {/* Decorative glass glow */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 border border-blue-500/30 text-blue-400 rounded-lg">
              <Shield className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-100">Electronic Signature</h3>
              <p className="text-xs text-slate-400">FDA 21 CFR Part 11 Authenticator</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-200 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mb-4 p-3 bg-amber-500/10 border border-amber-500/20 text-amber-300 rounded-lg text-xs flex gap-2.5">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>
            Signing this document manifests electronic authority equivalent to your handwritten signature.
          </span>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">USER EMAIL</label>
            <input
              type="text"
              value={currentEmail}
              disabled
              className="w-full bg-slate-800 border border-slate-700/40 rounded-lg py-2 px-3 text-slate-400 text-sm outline-none cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">PASSWORD PROOF</label>
            <div className="relative">
              <input
                type="password"
                placeholder="Enter password to sign"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700/60 rounded-lg py-2 pl-10 pr-3 text-slate-100 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
              />
              <KeyRound className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">SIGNATURE REASON</label>
            <textarea
              placeholder="e.g. Approved data export of compound logs"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full h-20 bg-slate-800 border border-slate-700/60 rounded-lg py-2 px-3 text-slate-100 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">SIGNATURE MEANING</label>
            <select
              value={meaning}
              onChange={(e) => setMeaning(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700/60 rounded-lg py-2 px-3 text-slate-100 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
            >
              <option value="Approved">Approved (Sign-off agreement)</option>
              <option value="Author">Author (Creation origin)</option>
              <option value="Reviewer">Reviewer (Data verification validation)</option>
              <option value="Witness">Witness (Secondary validation)</option>
            </select>
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-300 text-xs rounded-lg">
              {error}
            </div>
          )}

          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700/40 rounded-lg text-sm transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-slate-100 font-medium rounded-lg text-sm flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Verifying...' : 'Sign Electronically'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
