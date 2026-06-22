import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../../../services/api';
import { 
  Plug, ArrowRight, ArrowLeft, Check, AlertTriangle, 
  Upload, Key, Server
} from 'lucide-react';

export const AddConnectorWizard = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [capabilities, setCapabilities] = useState<any[]>([]);
  const [loadingCapabilities, setLoadingCapabilities] = useState(true);
  
  // Selection & form states
  const [selectedConnector, setSelectedConnector] = useState<any | null>(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [credentials, setCredentials] = useState<Record<string, any>>({});
  const [additionalParams, setAdditionalParams] = useState<Record<string, any>>({});
  
  // Test connection state
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchCaps = async () => {
      try {
        setLoadingCapabilities(true);
        const data = await apiRequest('/connectors/capabilities', { service: 'connectors' });
        setCapabilities(data);
      } catch (err) {
        console.error('Failed to load capabilities:', err);
      } finally {
        setLoadingCapabilities(false);
      }
    };
    fetchCaps();
  }, []);

  const handleConnectorSelect = (cap: any) => {
    setSelectedConnector(cap);
    setCredentials({});
    setAdditionalParams({});
    setTestResult(null);
    setStep(2);
  };

  const handleCredentialChange = (key: string, value: any) => {
    setCredentials(prev => ({ ...prev, [key]: value }));
  };

  const handleParamChange = (key: string, value: any) => {
    setAdditionalParams(prev => ({ ...prev, [key]: value }));
  };

  // Handles CSV / Excel upload converting it to base64
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      const b64 = (reader.result as string).split(',')[1];
      handleCredentialChange('file_name', file.name);
      handleCredentialChange('file_content', b64);
    };
    reader.readAsDataURL(file);
  };

  const handleTestConnection = async () => {
    if (!selectedConnector) return;
    setTesting(true);
    setTestResult(null);
    try {
      const result = await apiRequest('/connectors/test-raw', {
        method: 'POST',
        service: 'connectors',
        body: JSON.stringify({
          connector_type: selectedConnector.connector_type,
          credentials,
          additional_params: additionalParams
        })
      });
      setTestResult({ success: result.success, message: result.message });
    } catch (err: any) {
      setTestResult({ success: false, message: err.message || 'Verification failed.' });
    } finally {
      setTesting(false);
    }
  };

  const handleSaveConnection = async () => {
    if (!selectedConnector || !name.trim()) return;
    setSubmitting(true);
    try {
      await apiRequest('/connectors/sources', {
        method: 'POST',
        service: 'connectors',
        body: JSON.stringify({
          name,
          description,
          connector_type: selectedConnector.connector_type,
          credentials,
          additional_params: additionalParams,
          is_active: true
        })
      });
      // Redirect to dashboard
      navigate('/connectors');
    } catch (err: any) {
      alert(`Failed to save data source: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const isStep2Valid = () => {
    if (!selectedConnector) return false;
    for (const req of selectedConnector.required_credentials) {
      if (!credentials[req]) return false;
    }
    return true;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#1e293b] pb-5">
        <div>
          <span className="text-xs text-sky-400 font-bold uppercase tracking-widest">Setup Wizard</span>
          <h1 className="text-xl font-bold text-white mt-1">Connect New Data Stream</h1>
        </div>
        <button
          onClick={() => navigate('/connectors')}
          className="text-xs text-slate-400 hover:text-white transition-all font-semibold"
        >
          Cancel
        </button>
      </div>

      {/* Steps indicator */}
      <div className="flex items-center justify-between bg-[#0c1220] border border-[#1e293b] px-6 py-4 rounded-xl">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center space-x-2">
            <div className={`h-7 w-7 rounded-full flex items-center justify-center text-xs font-bold ${
              step === s
                ? 'bg-gradient-to-r from-sky-500 to-teal-500 text-white shadow-md'
                : step > s
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'bg-slate-800 text-slate-400'
            }`}>
              {step > s ? <Check className="h-4 w-4" /> : s}
            </div>
            <span className={`text-xs font-semibold ${step === s ? 'text-white' : 'text-slate-500'}`}>
              {s === 1 ? 'Choose Stream' : s === 2 ? 'Connection Settings' : 'Metadata Catalog'}
            </span>
            {s < 3 && <div className="h-0.5 w-16 bg-[#1e293b]" />}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <div className="bg-[#0c1220] border border-[#1e293b] p-6 rounded-2xl shadow-xl min-h-[300px] flex flex-col justify-between">
        
        {/* Step 1: Select Type */}
        {step === 1 && (
          <div className="space-y-4">
            <div className="border-b border-[#1e293b]/60 pb-3">
              <h2 className="text-base font-bold text-slate-200">Select Platform Type</h2>
              <p className="text-xs text-slate-400">Select the database architecture or software adapter to configure.</p>
            </div>
            
            {loadingCapabilities ? (
              <div className="flex justify-center items-center py-10 space-y-2 flex-col">
                <div className="h-8 w-8 rounded-full border-2 border-sky-500 border-t-transparent animate-spin"></div>
                <span className="text-xs text-slate-400">Querying registered adaptors...</span>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {capabilities.map((cap) => (
                  <div
                    key={cap.connector_type}
                    onClick={() => handleConnectorSelect(cap)}
                    className="p-5 border border-[#1e293b] bg-[#0c1220] hover:bg-[#101b30] hover:border-sky-500/40 rounded-xl transition-all cursor-pointer flex items-start space-x-3.5"
                  >
                    <div className="bg-sky-500/10 p-2.5 rounded-lg border border-sky-500/20 text-sky-400 shrink-0">
                      <Plug className="h-5 w-5" />
                    </div>
                    <div>
                      <h4 className="font-bold text-white text-sm">{cap.name}</h4>
                      <p className="text-xs text-slate-400 mt-1">{cap.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Step 2: Configure Credentials */}
        {step === 2 && selectedConnector && (
          <div className="space-y-5">
            <div className="border-b border-[#1e293b]/60 pb-3 flex justify-between items-center">
              <div>
                <h2 className="text-base font-bold text-slate-200">Configure {selectedConnector.name} Parameters</h2>
                <p className="text-xs text-slate-400">Complete connection credentials and authorization tokens.</p>
              </div>
              <span className="text-xs bg-slate-800 text-slate-300 font-bold px-2 py-0.5 rounded-md uppercase tracking-wider">
                {selectedConnector.connector_type}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Dynamic form based on required_credentials */}
              {selectedConnector.required_credentials.map((req: string) => (
                <div key={req} className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-400 capitalize">
                    {req.replace('_', ' ')}
                  </label>
                  
                  {req === 'file_content' ? (
                    <div className="flex items-center justify-center w-full">
                      <label className="flex flex-col items-center justify-center w-full h-28 border-2 border-dashed border-[#1e293b] hover:border-[#334155] rounded-xl cursor-pointer hover:bg-slate-800/10 transition-all">
                        <div className="flex flex-col items-center justify-center pt-5 pb-6">
                          <Upload className="h-6 w-6 text-slate-500 mb-2" />
                          <p className="text-xs text-slate-400">
                            {credentials['file_name'] ? (
                              <span className="font-mono text-emerald-400 font-semibold">{credentials['file_name']}</span>
                            ) : (
                              <span>Upload CSV / Excel dataset</span>
                            )}
                          </p>
                        </div>
                        <input type="file" className="hidden" accept=".csv,.xlsx,.xls" onChange={handleFileUpload} />
                      </label>
                    </div>
                  ) : req === 'password' || req === 'auth_token' ? (
                    <div className="flex items-center bg-[#070b13] border border-slate-800 focus-within:border-sky-500 rounded-xl px-3 py-2">
                      <Key className="h-4 w-4 text-slate-500 mr-2" />
                      <input
                        type="password"
                        placeholder="••••••••••••••"
                        value={credentials[req] || ''}
                        onChange={(e) => handleCredentialChange(req, e.target.value)}
                        className="bg-transparent text-sm text-slate-100 placeholder-slate-600 focus:outline-none w-full"
                      />
                    </div>
                  ) : (
                    <div className="flex items-center bg-[#070b13] border border-slate-800 focus-within:border-sky-500 rounded-xl px-3 py-2">
                      <Server className="h-4 w-4 text-slate-500 mr-2" />
                      <input
                        type="text"
                        placeholder={req === 'port' ? '5432' : req === 'host' ? '127.0.0.1' : `Enter ${req}`}
                        value={credentials[req] || ''}
                        onChange={(e) => handleCredentialChange(req, e.target.value)}
                        className="bg-transparent text-sm text-slate-100 placeholder-slate-600 focus:outline-none w-full"
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Simulator Option */}
            <div className="flex items-center space-x-2.5 bg-slate-950/40 border border-slate-800/80 p-3.5 rounded-xl">
              <input
                type="checkbox"
                id="use_simulator"
                checked={credentials['use_simulator'] !== false}
                onChange={(e) => handleCredentialChange('use_simulator', e.target.checked)}
                className="h-4.5 w-4.5 accent-sky-500 rounded cursor-pointer"
              />
              <div>
                <label htmlFor="use_simulator" className="text-xs font-bold text-slate-200 cursor-pointer block">
                  Enable Client Sandbox Simulator
                </label>
                <span className="text-[10px] text-slate-500 block">
                  Simulates realistic vendor API endpoints and returns unified test datasets offline.
                </span>
              </div>
            </div>

            {/* Vendor specific settings for LIMS/ELN/Assay/File */}
            {selectedConnector.connector_type === 'eln' && (
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400">Select Notebook Vendor</label>
                <select
                  value={additionalParams['vendor'] || 'benchling'}
                  onChange={(e) => {
                    handleParamChange('vendor', e.target.value);
                    if (!name) setName(`${e.target.value.toUpperCase()} ELN`);
                  }}
                  className="bg-[#070b13] border border-slate-800 text-sm text-slate-300 px-3 py-2 rounded-xl focus:border-sky-500 focus:outline-none w-full"
                >
                  <option value="benchling">Benchling SDK API</option>
                  <option value="dotmatics">Dotmatics ELN REST</option>
                  <option value="signals">Signals Notebook API</option>
                </select>
              </div>
            )}
            
            {selectedConnector.connector_type === 'lims' && (
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400">Select LIMS Vendor</label>
                <select
                  value={additionalParams['vendor'] || 'labvantage'}
                  onChange={(e) => {
                    handleParamChange('vendor', e.target.value);
                    if (!name) setName(`${e.target.value.toUpperCase()} LIMS`);
                  }}
                  className="bg-[#070b13] border border-slate-800 text-sm text-slate-300 px-3 py-2 rounded-xl focus:border-sky-500 focus:outline-none w-full"
                >
                  <option value="labvantage">LabVantage Web API</option>
                  <option value="labware">LabWare LIMS Adapter</option>
                  <option value="starlims">STARLIMS REST Service</option>
                </select>
              </div>
            )}

            {selectedConnector.connector_type === 'assay' && (
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400">Select Assay DB Type</label>
                <select
                  value={additionalParams['vendor'] || 'bioassay'}
                  onChange={(e) => {
                    handleParamChange('vendor', e.target.value);
                    if (!name) setName(`${e.target.value.toUpperCase()} Assay DB`);
                  }}
                  className="bg-[#070b13] border border-slate-800 text-sm text-slate-300 px-3 py-2 rounded-xl focus:border-sky-500 focus:outline-none w-full"
                >
                  <option value="bioassay">CDD Vault / BioAssay Database</option>
                  <option value="screening">Primary Assay Screening Database</option>
                  <option value="hts">High-Throughput Screening (HTS) System</option>
                </select>
              </div>
            )}

            {/* Test Connection Button */}
            <div className="pt-4 border-t border-[#1e293b]/60 flex items-center justify-between">
              <button
                type="button"
                onClick={handleTestConnection}
                disabled={testing || !isStep2Valid()}
                className="flex items-center space-x-1.5 bg-[#1a283d] hover:bg-[#20344d] border border-sky-500/20 text-sky-400 font-semibold text-xs px-4 py-2 rounded-lg transition-all disabled:opacity-40"
              >
                <span>{testing ? 'Testing connection...' : 'Test Connection'}</span>
              </button>

              {testResult && (
                <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg border text-xs font-medium ${
                  testResult.success 
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                    : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                }`}>
                  {testResult.success ? <Check className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
                  <span>{testResult.message}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Name and description */}
        {step === 3 && (
          <div className="space-y-5">
            <div className="border-b border-[#1e293b]/60 pb-3">
              <h2 className="text-base font-bold text-slate-200">Catalog Registry settings</h2>
              <p className="text-xs text-slate-400">Establish the display metadata parameters inside the Informatics platform.</p>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400">Display Name</label>
                <input
                  type="text"
                  placeholder="e.g. CDD Bioactivity Vault, Benchling Dev Environment"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="bg-[#070b13] border border-slate-800 focus:border-sky-500 rounded-xl px-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none w-full"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400">Description</label>
                <textarea
                  placeholder="Describe the scientific datasets available in this connection..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={4}
                  className="bg-[#070b13] border border-slate-800 focus:border-sky-500 rounded-xl px-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none w-full resize-none"
                />
              </div>
            </div>
          </div>
        )}

        {/* Navigation Bar */}
        <div className="mt-8 pt-5 border-t border-[#1e293b] flex justify-between items-center">
          {step > 1 ? (
            <button
              onClick={() => setStep(prev => prev - 1)}
              className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white font-semibold transition-all"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back</span>
            </button>
          ) : (
            <div />
          )}

          {step < 3 ? (
            <button
              onClick={() => setStep(prev => prev + 1)}
              disabled={step === 2 && !isStep2Valid()}
              className="flex items-center space-x-1.5 bg-[#1e293b] hover:bg-[#334155] text-white font-semibold text-xs px-4 py-2.5 rounded-lg border border-slate-700 transition-all disabled:opacity-40"
            >
              <span>Next</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          ) : (
            <button
              onClick={handleSaveConnection}
              disabled={submitting || !name.trim()}
              className="flex items-center space-x-1.5 bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-600 hover:to-teal-600 text-white font-semibold text-xs px-5 py-2.5 rounded-lg shadow-lg transition-all"
            >
              <span>{submitting ? 'Registering...' : 'Register Stream'}</span>
              <Check className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
