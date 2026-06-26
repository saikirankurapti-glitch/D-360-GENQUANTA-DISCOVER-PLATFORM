import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  BookOpen,
  X,
  Search,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Maximize2,
  Minimize2,
  Download,
  HelpCircle,
  FileText
} from 'lucide-react';

interface UserGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ManualPage {
  id: number;
  title: string;
  subtitle: string;
}

const manualPages: ManualPage[] = [
  { id: 1, title: '01. Dashboard Central', subtitle: 'Platform Command Manual Introduction' },
  { id: 2, title: 'Dashboard Usage & Metrics', subtitle: 'Pipeline status, success rates, and live system feed' },
  { id: 3, title: '02. Account Preferences', subtitle: 'Researcher profile and settings management' },
  { id: 4, title: '03. Target Explorer', subtitle: 'Structural retrieval engine for 3D protein structures' },
  { id: 5, title: '3D Protein Viewer', subtitle: 'Loading structures from database and UniProt scanning' },
  { id: 6, title: '04. Pocket Identification', subtitle: 'Real-time feedback & druggability probability mapping' },
  { id: 7, title: '05. AI Hit Screening', subtitle: 'Massive virtual screening with GNN models' },
  { id: 8, title: '06. Molecular Docking', subtitle: 'Physics-based simulation of receptor-ligand fit' },
  { id: 9, title: 'Docking Simulation & Output', subtitle: 'SMILES input, Vina logs, and binding energy/potency' },
  { id: 10, title: '07. Lead Optimization', subtitle: 'Generative AI models for binding affinity evolution' },
  { id: 11, title: '08. ADMET Prediction', subtitle: 'Pharmacokinetic profiling & absorption prediction' },
  { id: 12, title: '09. Preformulation Properties', subtitle: 'Stability assessment & thermodynamic profiling' },
  { id: 13, title: 'Physicochemical Stability', subtitle: 'Solvent compatibility, Lipinski rules, and degradation' },
  { id: 14, title: '10. Formulation Design', subtitle: 'AI-optimized ingredient ratios & excipient compatibility' },
  { id: 15, title: 'Formulation Optimization Steps', subtitle: 'Target dosage, dissolution, and shelf-life optimization' },
  { id: 16, title: '11. Blinded Results Review', subtitle: 'Anonymized performance metrics for unbiased review' },
  { id: 17, title: '12. Robotic Validation', subtitle: 'Autonomous liquid handling & Opentrons OT-2 setup' },
  { id: 18, title: 'Autonomous Robotic Code Generation', subtitle: 'AI-generated Python protocols for robotic actions' },
  { id: 19, title: '13. Discovery Reports', subtitle: 'Exporting 3D snapshots, safety scores, and intelligence logs' },
  { id: 20, title: '14. Workflow Shortcuts', subtitle: 'Jump to Lab: transition from optimization to wet lab validation' },
  { id: 21, title: 'Workflow Jumps & Support Details', subtitle: 'Workflow jump to Docking verification and contact channel' }
];

export const UserGuideModal: React.FC<UserGuideModalProps> = ({ isOpen, onClose }) => {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [imageLoaded, setImageLoaded] = useState<boolean>(false);
  
  const imageContainerRef = useRef<HTMLDivElement>(null);
  const sidebarRef = useRef<HTMLDivElement>(null);
  const activeItemRef = useRef<HTMLButtonElement>(null);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.key === 'Escape') {
        if (isFullscreen) {
          setIsFullscreen(false);
        } else {
          onClose();
        }
      } else if (e.key === 'ArrowRight') {
        handleNextPage();
      } else if (e.key === 'ArrowLeft') {
        handlePrevPage();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, currentPage, isFullscreen]);

  // Reset zoom on page change
  useEffect(() => {
    setZoomLevel(1);
    setImageLoaded(false);
  }, [currentPage]);

  // Center scroll active page in sidebar
  useEffect(() => {
    if (activeItemRef.current && sidebarRef.current) {
      const sidebar = sidebarRef.current;
      const activeItem = activeItemRef.current;
      
      const sidebarTop = sidebar.scrollTop;
      const sidebarBottom = sidebarTop + sidebar.clientHeight;
      const itemTop = activeItem.offsetTop;
      const itemBottom = itemTop + activeItem.clientHeight;
      
      if (itemTop < sidebarTop || itemBottom > sidebarBottom) {
        sidebar.scrollTo({
          top: itemTop - sidebar.clientHeight / 2 + activeItem.clientHeight / 2,
          behavior: 'smooth'
        });
      }
    }
  }, [currentPage]);

  const handleNextPage = () => {
    setCurrentPage((prev) => (prev < 21 ? prev + 1 : prev));
  };

  const handlePrevPage = () => {
    setCurrentPage((prev) => (prev > 1 ? prev - 1 : prev));
  };

  const handleZoomIn = () => {
    setZoomLevel((prev) => Math.min(prev + 0.25, 3));
  };

  const handleZoomOut = () => {
    setZoomLevel((prev) => Math.max(prev - 0.25, 0.75));
  };

  const handleResetZoom = () => {
    setZoomLevel(1);
  };

  const filteredPages = useMemo(() => {
    if (!searchQuery.trim()) return manualPages;
    const query = searchQuery.toLowerCase();
    return manualPages.filter(
      (page) =>
        page.title.toLowerCase().includes(query) ||
        page.subtitle.toLowerCase().includes(query) ||
        page.id.toString() === query
    );
  }, [searchQuery]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-6 bg-slate-950/85 backdrop-blur-sm animate-fade-in">
      {/* Modal Inner Container */}
      <div 
        className={`bg-[#0b0f19] border border-slate-800 rounded-2xl flex flex-col w-full h-[90vh] overflow-hidden shadow-[0_0_50px_-12px_rgba(16,185,129,0.25)] transition-all duration-300 ${
          isFullscreen ? 'max-w-none h-screen rounded-none border-none p-0' : 'max-w-7xl'
        }`}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-[#0d1321] select-none">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <BookOpen className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                AnalytiX
                <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-normal">
                  User Guide v4.0
                </span>
              </h3>
              <p className="text-xs text-slate-400">Platform Command Manual & Scientific Workflows</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Download Manual Link */}
            <a
              href="/manual_pages/analytix_platform.pdf"
              download="analytix_platform.pdf"
              className="flex items-center space-x-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 hover:border-emerald-500/30 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all shadow-sm cursor-pointer"
              title="Download full PDF manual"
            >
              <Download className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Download PDF</span>
            </a>
            
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 rounded-lg transition-colors border border-transparent hover:border-slate-700/50"
              title="Close User Manual"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Modal Main Content Workspace */}
        <div className="flex flex-1 overflow-hidden">
          
          {/* Left Sidebar - Navigation Index */}
          <div className="w-80 border-r border-slate-800 bg-[#080c14] flex flex-col shrink-0 select-none">
            {/* Search Input */}
            <div className="p-4 border-b border-slate-800">
              <div className="relative">
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search manual topics..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-[#0d1321] border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all"
                />
              </div>
            </div>

            {/* Scrollable List of Pages */}
            <div 
              ref={sidebarRef}
              className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar"
            >
              {filteredPages.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-center px-4">
                  <HelpCircle className="h-8 w-8 text-slate-600 mb-2" />
                  <p className="text-sm text-slate-400 font-medium">No sections found</p>
                  <p className="text-xs text-slate-500 mt-1">Try matching section names or numbers</p>
                </div>
              ) : (
                filteredPages.map((page) => {
                  const isActive = page.id === currentPage;
                  return (
                    <button
                      key={page.id}
                      ref={isActive ? activeItemRef : null}
                      onClick={() => setCurrentPage(page.id)}
                      className={`w-full text-left p-3 rounded-lg flex items-start space-x-3 transition-all ${
                        isActive
                          ? 'bg-gradient-to-r from-emerald-950/40 to-slate-900 border-l-2 border-emerald-500 text-slate-100 shadow-sm'
                          : 'hover:bg-slate-900/60 text-slate-400 hover:text-slate-200 border-l-2 border-transparent'
                      }`}
                    >
                      <div className={`h-6 w-6 rounded-md shrink-0 flex items-center justify-center font-bold text-xs ${
                        isActive ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-850 text-slate-500'
                      }`}>
                        {page.id}
                      </div>
                      <div className="min-w-0">
                        <p className={`text-xs font-semibold truncate ${isActive ? 'text-slate-100' : 'text-slate-300'}`}>
                          {page.title}
                        </p>
                        <p className="text-[10px] text-slate-500 line-clamp-1 mt-0.5 leading-normal">
                          {page.subtitle}
                        </p>
                      </div>
                    </button>
                  );
                })
              )}
            </div>

            {/* Bottom Help Note */}
            <div className="p-3 bg-[#0d1321] border-t border-slate-800 text-[10px] text-slate-500 flex items-center gap-2 select-none">
              <FileText className="h-3.5 w-3.5 text-slate-400" />
              <span>Use Left/Right arrows to flip pages.</span>
            </div>
          </div>

          {/* Right Area - Document Image Viewer */}
          <div className="flex-1 flex flex-col bg-[#05080e] overflow-hidden relative">
            
            {/* Viewer Top Toolbar */}
            <div className="flex items-center justify-between px-6 py-2.5 bg-[#090d16] border-b border-slate-800 select-none">
              <div className="flex items-center space-x-2">
                <button
                  onClick={handlePrevPage}
                  disabled={currentPage === 1}
                  className="p-1.5 text-slate-400 hover:text-slate-100 disabled:text-slate-650 hover:bg-slate-800 rounded transition-colors disabled:hover:bg-transparent"
                  title="Previous Page"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                <span className="text-xs font-bold text-slate-300 min-w-[70px] text-center bg-[#0d1321] px-2.5 py-1 rounded border border-slate-800">
                  Page {currentPage} of 21
                </span>
                <button
                  onClick={handleNextPage}
                  disabled={currentPage === 21}
                  className="p-1.5 text-slate-400 hover:text-slate-100 disabled:text-slate-650 hover:bg-slate-800 rounded transition-colors disabled:hover:bg-transparent"
                  title="Next Page"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>

              {/* Center Page Title Display */}
              <div className="hidden lg:block text-xs font-semibold text-slate-400 max-w-sm truncate">
                {manualPages[currentPage - 1]?.title}
              </div>

              {/* View Control Buttons */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleZoomOut}
                  className="p-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded transition-colors"
                  title="Zoom Out"
                >
                  <ZoomOut className="h-4 w-4" />
                </button>
                <span className="text-[10px] font-bold text-slate-400 w-12 text-center select-none">
                  {Math.round(zoomLevel * 100)}%
                </span>
                <button
                  onClick={handleZoomIn}
                  className="p-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded transition-colors"
                  title="Zoom In"
                >
                  <ZoomIn className="h-4 w-4" />
                </button>
                <button
                  onClick={handleResetZoom}
                  disabled={zoomLevel === 1}
                  className="p-1.5 text-slate-400 hover:text-slate-100 disabled:text-slate-600 hover:bg-slate-800 rounded transition-colors disabled:hover:bg-transparent"
                  title="Reset Zoom"
                >
                  <RotateCcw className="h-4 w-4" />
                </button>
                <div className="h-4 w-px bg-slate-800 mx-1"></div>
                <button
                  onClick={() => setIsFullscreen(!isFullscreen)}
                  className="p-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded transition-colors"
                  title={isFullscreen ? "Exit Fullscreen" : "Fullscreen Viewer"}
                >
                  {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* Main Interactive Screen */}
            <div 
              ref={imageContainerRef}
              className="flex-1 overflow-auto p-6 md:p-8 flex items-start justify-center custom-scrollbar select-none bg-[#030509]"
            >
              <div 
                className="relative bg-white shadow-2xl rounded-lg border border-slate-900 transition-all duration-300"
                style={{
                  transform: `scale(${zoomLevel})`,
                  transformOrigin: 'top center',
                  maxWidth: '100%',
                  width: '850px' // optimal resolution width matching rendered fits
                }}
              >
                {!imageLoaded && (
                  <div className="absolute inset-0 bg-[#090d16] flex flex-col items-center justify-center text-slate-400 rounded-lg">
                    <div className="h-8 w-8 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin mb-3"></div>
                    <span className="text-xs font-semibold text-slate-500">Loading Page Asset...</span>
                  </div>
                )}
                
                <img
                  src={`/manual_pages/page_${currentPage}.png`}
                  alt={`Platform User Manual - Page ${currentPage}`}
                  onLoad={() => setImageLoaded(true)}
                  className={`w-full h-auto select-none rounded-lg pointer-events-none transition-opacity duration-300 ${
                    imageLoaded ? 'opacity-100' : 'opacity-0'
                  }`}
                  style={{ display: 'block' }}
                />
              </div>
            </div>

            {/* Quick Navigation Slider */}
            <div className="px-6 py-2 bg-[#090d16] border-t border-slate-800 select-none flex items-center space-x-3 overflow-x-auto shrink-0 custom-scrollbar">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider shrink-0">Quick Flip:</span>
              <div className="flex space-x-1.5 py-1">
                {Array.from({ length: 21 }, (_, i) => i + 1).map((pageNum) => {
                  const isCurrent = pageNum === currentPage;
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`h-6 w-7 rounded font-bold text-[10px] transition-all flex items-center justify-center shrink-0 border ${
                        isCurrent
                          ? 'bg-emerald-500 text-slate-950 border-emerald-400'
                          : 'bg-[#0d1321] text-slate-400 border-slate-800 hover:border-slate-650 hover:text-slate-200'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>
            </div>

          </div>

        </div>
      </div>
    </div>
  );
};
