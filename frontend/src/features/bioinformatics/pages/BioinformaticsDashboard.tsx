import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Dna, GitMerge, ChevronRight, Binary } from 'lucide-react';

export const BioinformaticsDashboard: React.FC = () => {
  const navigate = useNavigate();

  const cards = [
    {
      title: 'Sequence Explorer',
      description: 'Upload FASTA files, inspect DNA/RNA/Protein sequences, and calculate parameters like molecular weight and isoelectric point.',
      path: '/sequences',
      icon: Dna,
      color: 'from-blue-500 to-indigo-500'
    },
    {
      title: 'Sequence Alignment Studio',
      description: 'Perform Pairwise (Global/Local) and Multiple Sequence Alignment (MSA) with detailed Clustal consensus printouts.',
      path: '/alignments',
      icon: Binary,
      color: 'from-emerald-500 to-teal-500'
    },
    {
      title: 'Sequence Clustering Center',
      description: 'Run hierarchical clustering to compile sequence identity distance matrices and interactive dendrogram heatmaps.',
      path: '/clusters',
      icon: GitMerge,
      color: 'from-purple-500 to-pink-500'
    }
  ];

  return (
    <div className="space-y-8 max-w-6xl mx-auto py-4">
      {/* Intro Hero */}
      <div className="relative overflow-hidden bg-slate-900/40 border border-slate-800/80 rounded-3xl p-8 backdrop-blur-md">
        <div className="absolute top-0 right-0 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full text-xs font-semibold text-blue-400">
            <Dna className="w-3.5 h-3.5 animate-pulse" />
            Biological Informatics Suite
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Biology & Bioinformatics Platform
          </h1>
          <p className="text-sm text-slate-400 max-w-2xl leading-relaxed">
            Sequence management, molecular parameter analysis, pairwise/multiple sequence alignment, and distance-based phylogenetic clustering algorithms.
          </p>
        </div>
      </div>

      {/* Capabilities Navigation */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {cards.map((c) => {
          const Icon = c.icon;
          return (
            <button
              key={c.title}
              onClick={() => navigate(c.path)}
              className="group text-left relative overflow-hidden bg-slate-900/35 hover:bg-slate-900/50 border border-slate-800/60 hover:border-slate-700/80 p-6 rounded-2xl transition-all duration-300 flex flex-col justify-between h-64 hover:-translate-y-1 hover:shadow-xl hover:shadow-blue-500/5"
            >
              <div>
                <div className={`inline-flex p-3 bg-gradient-to-br ${c.color} text-white rounded-xl mb-4 group-hover:scale-110 transition-transform duration-300`}>
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-slate-100 group-hover:text-blue-400 transition-colors">
                  {c.title}
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  {c.description}
                </p>
              </div>
              <div className="flex items-center gap-1 text-xs font-semibold text-slate-400 group-hover:text-white transition-colors self-end mt-4">
                Enter Studio
                <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
