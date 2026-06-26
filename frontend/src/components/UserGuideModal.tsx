import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BookOpen, 
  X, 
  Download, 
  ExternalLink, 
  HelpCircle,
  FileText, 
  Sparkles, 
  ShieldCheck, 
  Zap,
  ArrowRight
} from 'lucide-react';

interface UserGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface CategoryCard {
  title: string;
  subtitle: string;
  description: string;
  fileName: string;
  icon: React.ComponentType<any>;
  color: string;
  bgColor: string;
  borderColor: string;
}

export const UserGuideModal: React.FC<UserGuideModalProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();

  if (!isOpen) return null;

  const categories: CategoryCard[] = [
    {
      title: "Master User Manual",
      subtitle: "Comprehensive Platform Reference",
      description: "Full operational reference, explaining all 20 modules, workflows, error handling, and scientific principles.",
      fileName: "AnalytiX_USER_MANUAL.pdf",
      icon: BookOpen,
      color: "text-emerald-400",
      bgColor: "bg-emerald-500/10",
      borderColor: "border-emerald-500/25"
    },
    {
      title: "Quick Start Guide",
      subtitle: "Rapid Scientific Onboarding",
      description: "Step-by-step instructions for performing structure searches, FASTA alignments, and running AI copilot commands.",
      fileName: "AnalytiX_QUICK_START_GUIDE.pdf",
      icon: Zap,
      color: "text-sky-400",
      bgColor: "bg-sky-500/10",
      borderColor: "border-sky-500/25"
    },
    {
      title: "System Admin Guide",
      subtitle: "Configuration & Compliance Control",
      description: "Detailed administration procedures including user invitations, RBAC matrices, and data connector configurations.",
      fileName: "AnalytiX_ADMIN_GUIDE.pdf",
      icon: ShieldCheck,
      color: "text-amber-400",
      bgColor: "bg-amber-500/10",
      borderColor: "border-amber-500/25"
    },
    {
      title: "AI Scientist Copilot Guide",
      subtitle: "Natural Language Grounding & Prompts",
      description: "Reference guide for scientific prompting, grounding rules, SQL generation parameters, and semantic search examples.",
      fileName: "AnalytiX_AI_COPILOT_GUIDE.pdf",
      icon: Sparkles,
      color: "text-indigo-400",
      bgColor: "bg-indigo-500/10",
      borderColor: "border-indigo-500/25"
    },
    {
      title: "E2E Test Execution Report",
      subtitle: "Automated Quality & Compliance Audit",
      description: "Cryptographically verified validation results with captured execution screenshots for all 14 core modules.",
      fileName: "AnalytiX_E2E_TEST_REPORT.pdf",
      icon: FileText,
      color: "text-rose-400",
      bgColor: "bg-rose-500/10",
      borderColor: "border-rose-500/25"
    }
  ];

  const handleOpenPDF = (fileName: string) => {
    window.open(`/docs/${fileName}`, '_blank');
  };

  const handleDownloadPDF = (fileName: string) => {
    const link = document.createElement('a');
    link.href = `/docs/${fileName}`;
    link.download = fileName;
    link.click();
  };

  const handleGoToPortal = () => {
    onClose();
    navigate('/user-guide');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-6 bg-slate-950/85 backdrop-blur-sm animate-fade-in select-none">
      {/* Modal Container */}
      <div className="bg-[#0b0f19] border border-slate-800 rounded-2xl flex flex-col w-full max-w-4xl max-h-[90vh] overflow-hidden shadow-[0_0_50px_-12px_rgba(14,165,233,0.2)]">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-[#0d1321]">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400">
              <BookOpen className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                AnalytiX Documentation Suite
                <span className="text-xs px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20 font-normal">
                  v4.0.0
                </span>
              </h3>
              <p className="text-xs text-slate-400">FDA 21 CFR Part 11 Compliant Environment Guides</p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 rounded-lg transition-colors border border-transparent hover:border-slate-700/50"
            title="Close modal"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 bg-[#080c14] custom-scrollbar">
          
          {/* Main prompt grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {categories.map((cat, index) => {
              const Icon = cat.icon;
              const isFullWidth = index === categories.length - 1 && categories.length % 2 !== 0;
              return (
                <div 
                  key={index} 
                  className={`p-5 rounded-xl border border-slate-800 bg-[#0c1220]/60 hover:bg-[#0c1220] hover:border-slate-700/50 flex flex-col justify-between transition-all group ${
                    isFullWidth ? 'md:col-span-2' : ''
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className={`p-2 rounded-lg ${cat.bgColor} border ${cat.borderColor} ${cat.color}`}>
                        <Icon className="h-5 w-5" />
                      </div>
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">PDF GUIDE</span>
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-slate-100">{cat.title}</h4>
                      <p className="text-[11px] text-sky-400/90 font-medium mt-0.5">{cat.subtitle}</p>
                      <p className="text-xs text-slate-400 mt-2 leading-relaxed">{cat.description}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 mt-5 pt-3 border-t border-slate-800/60 select-none">
                    <button
                      onClick={() => handleOpenPDF(cat.fileName)}
                      className="flex-1 flex items-center justify-center space-x-1.5 bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-500/20 hover:border-sky-500/30 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shadow-sm cursor-pointer"
                      title={`Open ${cat.title} in a new browser tab`}
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                      <span>Open PDF</span>
                    </button>
                    <button
                      onClick={() => handleDownloadPDF(cat.fileName)}
                      className="flex items-center justify-center bg-slate-800 hover:bg-slate-750 text-slate-300 hover:text-slate-100 border border-slate-700 px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
                      title="Download PDF"
                    >
                      <Download className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Quick link to the Inline Portal */}
          <div className="p-4 rounded-xl border border-sky-500/10 bg-sky-500/5 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400 shrink-0">
                <FileText className="h-5 w-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-100">Looking for the interactive Documentation Portal?</h4>
                <p className="text-xs text-slate-450 mt-0.5 leading-relaxed">
                  Browse topics, workflows, component specifications, and FAQ articles online directly in the platform.
                </p>
              </div>
            </div>
            
            <button
              onClick={handleGoToPortal}
              className="flex items-center space-x-1.5 bg-[#edf7f2] hover:bg-[#e1f0e7] text-[#0f766e] px-4.5 py-2 rounded-full text-xs font-bold transition-all shadow-sm border border-[#cedfd5] shrink-0 cursor-pointer"
            >
              <span>Explore Portal</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>

        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 bg-[#0d1321] border-t border-slate-800 text-[10px] text-slate-500 flex items-center justify-between">
          <span className="flex items-center gap-1">
            <HelpCircle className="h-3.5 w-3.5 text-slate-450" />
            Need advanced setup support? Contact IT Service Desk.
          </span>
          <span>© 2026 AnalytiX Inc.</span>
        </div>

      </div>
    </div>
  );
};
