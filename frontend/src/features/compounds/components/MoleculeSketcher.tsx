import { useEffect, useRef, useState } from 'react';
import { Sparkles, Trash2, Database } from 'lucide-react';

interface MoleculeSketcherProps {
  value: string;
  onChange: (smiles: string) => void;
  title?: string;
}

export const MoleculeSketcher = ({ value, onChange, title = 'Structure Designer' }: MoleculeSketcherProps) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [internalSmiles, setInternalSmiles] = useState('');

  // Handle incoming messages from JSME iframe
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data && event.data.type === 'JSME_SMILES_CHANGED') {
        const receivedSmiles = event.data.smiles || '';
        setInternalSmiles(receivedSmiles);
        onChange(receivedSmiles);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [onChange]);

  // Synchronize value changes from parent down to JSME iframe
  useEffect(() => {
    if (value !== internalSmiles && iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage(
        { type: 'JSME_SET_SMILES', smiles: value },
        '*'
      );
      setInternalSmiles(value);
    }
  }, [value]);

  const handleClear = () => {
    if (iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage(
        { type: 'JSME_SET_SMILES', smiles: '' },
        '*'
      );
    }
    setInternalSmiles('');
    onChange('');
  };

  const loadPreset = (smiles: string) => {
    if (iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage(
        { type: 'JSME_SET_SMILES', smiles },
        '*'
      );
    }
    setInternalSmiles(smiles);
    onChange(smiles);
  };

  const presets = [
    { name: 'Benzene', smiles: 'c1ccccc1' },
    { name: 'Pyridine', smiles: 'c1ccncc1' },
    { name: 'Aspirin', smiles: 'CC(=O)Oc1ccccc1C(=O)O' },
    { name: 'Indole', smiles: 'c1ccc2c(c1)[nH]cc2' },
  ];

  return (
    <div className="bg-[#0c1220] border border-slate-800 rounded-2xl p-4 flex flex-col space-y-3 shadow-lg h-full">
      <div className="flex justify-between items-center border-b border-slate-850 pb-2">
        <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
          <Sparkles className="h-3.5 w-3.5 text-sky-400" />
          <span>{title}</span>
        </h4>
        <button
          onClick={handleClear}
          className="text-slate-500 hover:text-rose-400 transition-colors p-1 rounded hover:bg-slate-800 cursor-pointer"
          title="Clear canvas"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      {/* Standalone sandboxed iframe */}
      <div className="flex-1 min-h-[300px] relative bg-[#070b13] rounded-xl overflow-hidden border border-slate-900">
        <iframe
          ref={iframeRef}
          src="/jsme.html"
          className="w-full h-full border-none"
          title="JSME Molecular Canvas"
        />
      </div>

      {/* Preset Chips */}
      <div className="flex flex-wrap gap-1.5 pt-1">
        <span className="text-[9px] text-slate-500 font-bold uppercase py-1 mr-1 flex items-center">
          <Database className="h-2.5 w-2.5 mr-1 text-slate-600" /> presets:
        </span>
        {presets.map((preset) => (
          <button
            key={preset.name}
            onClick={() => loadPreset(preset.smiles)}
            className="text-[9px] bg-[#131b2e] hover:bg-[#1a253f] border border-slate-800 hover:border-slate-700 text-slate-300 font-medium px-2 py-0.5 rounded transition-all cursor-pointer"
          >
            {preset.name}
          </button>
        ))}
      </div>
    </div>
  );
};
