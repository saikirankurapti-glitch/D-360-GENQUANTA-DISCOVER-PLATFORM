import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiRequest } from '../../../services/api';
import { 
  ArrowLeft, Database, Key, Columns, Eye, Link2, Plus, 
  Trash2, AlertCircle, Info, RefreshCw, Layers
} from 'lucide-react';

export const SchemaDiscoveryView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [source, setSource] = useState<any | null>(null);
  const [entities, setEntities] = useState<any[]>([]);
  const [selectedEntity, setSelectedEntity] = useState<any | null>(null);
  const [previewData, setPreviewData] = useState<{ columns: string[]; rows: any[][] } | null>(null);
  const [relationships, setRelationships] = useState<any[]>([]);
  
  // Loading states
  const [loading, setLoading] = useState(true);
  const [loadingPreview, setLoadingPreview] = useState(false);
  
  // Add Relationship Form
  const [sourceField, setSourceField] = useState('');
  const [targetEntity, setTargetEntity] = useState('');
  const [targetField, setTargetField] = useState('');
  const [cardinality, setCardinality] = useState('one_to_many');
  
  const [activeTab, setActiveTab] = useState<'fields' | 'preview' | 'relationships'>('fields');

  const fetchSchemaInfo = async () => {
    try {
      setLoading(true);
      const src = await apiRequest(`/connectors/sources/${id}`, { service: 'connectors' });
      const ents = await apiRequest(`/connectors/sources/${id}/entities`, { service: 'connectors' });
      const rels = await apiRequest(`/connectors/sources/${id}/relationships`, { service: 'connectors' });
      
      setSource(src);
      setEntities(ents);
      setRelationships(rels);
      
      if (ents.length > 0) {
        setSelectedEntity(ents[0]);
      }
    } catch (err) {
      console.error('Failed to load schema discovery:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPreview = async (entityName: string) => {
    setLoadingPreview(true);
    setPreviewData(null);
    try {
      const data = await apiRequest(`/connectors/sources/${id}/preview/${entityName}?limit=10`, {
        service: 'connectors'
      });
      setPreviewData(data);
    } catch (err) {
      console.error('Failed to fetch data preview:', err);
    } finally {
      setLoadingPreview(false);
    }
  };

  useEffect(() => {
    fetchSchemaInfo();
  }, [id]);

  useEffect(() => {
    if (selectedEntity) {
      if (activeTab === 'preview') {
        fetchPreview(selectedEntity.physical_name);
      }
      // Reset relationship form fields
      setSourceField('');
      setTargetEntity('');
      setTargetField('');
    }
  }, [selectedEntity, activeTab]);

  const handleCreateRelationship = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedEntity || !sourceField || !targetEntity || !targetField) return;

    try {
      const newRel = await apiRequest(`/connectors/sources/${id}/relationships`, {
        method: 'POST',
        service: 'connectors',
        body: JSON.stringify({
          source_entity_id: selectedEntity.id,
          source_field_id: parseInt(sourceField),
          target_entity_id: parseInt(targetEntity),
          target_field_id: parseInt(targetField),
          cardinality
        })
      });
      setRelationships([...relationships, newRel]);
      alert('Logical relationship successfully registered!');
      // Reset form
      setSourceField('');
      setTargetEntity('');
      setTargetField('');
    } catch (err: any) {
      alert(`Failed to save relationship: ${err.message}`);
    }
  };

  const handleDeleteRelationship = async (relId: number) => {
    if (!confirm('Are you sure you want to remove this logical link?')) return;
    try {
      await apiRequest(`/connectors/sources/${id}/relationships/${relId}`, {
        method: 'DELETE',
        service: 'connectors'
      });
      setRelationships(relationships.filter(r => r.id !== relId));
    } catch (err: any) {
      alert(`Deletion failed: ${err.message}`);
    }
  };

  // Find target entity fields for relationship creation dropdown
  const getTargetFields = () => {
    const target = entities.find(e => e.id === parseInt(targetEntity));
    return target ? target.fields : [];
  };

  const getEntityDisplayName = (entityId: number) => {
    const ent = entities.find(e => e.id === entityId);
    return ent ? ent.display_name : `Entity ID: ${entityId}`;
  };

  const getFieldDisplayName = (entityId: number, fieldId: number) => {
    const ent = entities.find(e => e.id === entityId);
    if (!ent) return `Field ID: ${fieldId}`;
    const fld = ent.fields.find((f: any) => f.id === fieldId);
    return fld ? fld.display_name : `Field ID: ${fieldId}`;
  };

  return (
    <div className="space-y-6 h-full flex flex-col">
      {/* Top Navigation Row */}
      <div className="flex items-center justify-between border-b border-[#1e293b] pb-4">
        <div className="flex items-center space-x-3">
          <button
            onClick={() => navigate('/connectors')}
            className="p-2 border border-[#1e293b] hover:border-[#334155] rounded-xl hover:bg-slate-800/10 text-slate-400 hover:text-white transition-all cursor-pointer"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-white flex items-center space-x-2">
              <Database className="h-5.5 w-5.5 text-sky-400" />
              <span>Dataset Browser</span>
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Source: <span className="text-sky-400 font-semibold">{source?.name}</span> ({source?.connector_type})
            </p>
          </div>
        </div>
        
        <button
          onClick={fetchSchemaInfo}
          className="flex items-center space-x-1 border border-slate-800 bg-[#0c1220] hover:bg-[#131b2e] px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 transition-all cursor-pointer"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Reload Catalog</span>
        </button>
      </div>

      {loading ? (
        <div className="flex-1 flex flex-col justify-center items-center space-y-3">
          <div className="h-10 w-10 rounded-full border-2 border-sky-500 border-t-transparent animate-spin"></div>
          <span className="text-sm text-slate-400">Inspecting catalog schema...</span>
        </div>
      ) : entities.length === 0 ? (
        <div className="flex-1 flex flex-col justify-center items-center text-center p-12 border border-dashed border-[#1e293b] rounded-2xl space-y-4">
          <AlertCircle className="h-12 w-12 text-rose-500" />
          <div>
            <h3 className="font-semibold text-lg text-slate-200">No Discovered Schema</h3>
            <p className="text-sm text-slate-500 max-w-sm mt-1">
              You must trigger schema synchronization on the dashboard before you can inspect columns.
            </p>
          </div>
          <button
            onClick={() => navigate('/connectors')}
            className="bg-[#1e293b] text-slate-200 px-5 py-2 rounded-xl text-sm font-semibold transition-all"
          >
            Return to Dashboard
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-0">
          {/* Discovered Entities Sidebar */}
          <div className="bg-[#0c1220] border border-[#1e293b] rounded-2xl p-4 overflow-y-auto">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center space-x-1.5">
              <Layers className="h-3.5 w-3.5 text-teal-400" />
              <span>Catalog Tables ({entities.length})</span>
            </h3>
            
            <div className="space-y-1.5">
              {entities.map((entity) => (
                <div
                  key={entity.id}
                  onClick={() => setSelectedEntity(entity)}
                  className={`p-3 rounded-xl cursor-pointer transition-all border text-sm font-semibold flex items-center justify-between ${
                    selectedEntity?.id === entity.id
                      ? 'bg-[#101b30] border-sky-500/50 text-white shadow-md'
                      : 'bg-transparent border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/10'
                  }`}
                >
                  <span className="truncate">{entity.display_name}</span>
                  <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full shrink-0 font-bold ml-2">
                    {entity.fields.length}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Details and Actions Area */}
          <div className="lg:col-span-3 details-panel-span flex flex-col bg-[#0c1220] border border-[#1e293b] rounded-2xl overflow-hidden min-h-0">
            {selectedEntity ? (
              <>
                {/* Tabs Header */}
                <div className="flex border-b border-[#1e293b] bg-[#0c1220]/60 px-6 pt-3 space-x-6">
                  <button
                    onClick={() => setActiveTab('fields')}
                    className={`pb-3 text-sm font-bold flex items-center space-x-1.5 border-b-2 transition-all cursor-pointer ${
                      activeTab === 'fields'
                        ? 'border-sky-500 text-white'
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Columns className="h-4 w-4" />
                    <span>Columns Catalog</span>
                  </button>
                  
                  <button
                    onClick={() => setActiveTab('preview')}
                    className={`pb-3 text-sm font-bold flex items-center space-x-1.5 border-b-2 transition-all cursor-pointer ${
                      activeTab === 'preview'
                        ? 'border-sky-500 text-white'
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Eye className="h-4 w-4" />
                    <span>Data Preview</span>
                  </button>
                  
                  <button
                    onClick={() => setActiveTab('relationships')}
                    className={`pb-3 text-sm font-bold flex items-center space-x-1.5 border-b-2 transition-all cursor-pointer ${
                      activeTab === 'relationships'
                        ? 'border-sky-500 text-white'
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Link2 className="h-4 w-4" />
                    <span>Cross-Entity Relations</span>
                  </button>
                </div>

                {/* Tab Contents */}
                <div className="flex-1 overflow-y-auto p-6 min-h-0">
                  {/* Columns Catalog Tab */}
                  {activeTab === 'fields' && (
                    <div className="space-y-4">
                      <div>
                        <h2 className="text-base font-bold text-white">{selectedEntity.display_name} Columns</h2>
                        <p className="text-xs text-slate-400 mt-0.5">{selectedEntity.description || 'No description available.'}</p>
                      </div>

                      <div className="border border-[#1e293b] rounded-xl overflow-hidden bg-[#070b13]/20">
                        <table className="w-full text-left border-collapse text-xs">
                          <thead>
                            <tr className="border-b border-[#1e293b] bg-slate-900/60 text-slate-400 font-bold uppercase tracking-wider">
                              <th className="p-3">Physical Name</th>
                              <th className="p-3">Display Label</th>
                              <th className="p-3">Data Type</th>
                              <th className="p-3 text-center">Keys</th>
                              <th className="p-3 text-center">Nullable</th>
                            </tr>
                          </thead>
                          <tbody>
                            {selectedEntity.fields.map((field: any) => (
                              <tr key={field.id} className="border-b border-[#1e293b]/50 hover:bg-slate-800/10">
                                <td className="p-3 font-mono text-slate-300 font-medium">{field.physical_name}</td>
                                <td className="p-3 font-semibold text-white">{field.display_name}</td>
                                <td className="p-3 text-slate-400">{field.data_type}</td>
                                <td className="p-3 text-center">
                                  {field.is_primary_key && (
                                    <span className="inline-flex items-center space-x-0.5 bg-sky-500/10 text-sky-400 border border-sky-500/20 px-2 py-0.5 rounded-full font-bold">
                                      <Key className="h-3 w-3 shrink-0" />
                                      <span>PK</span>
                                    </span>
                                  )}
                                </td>
                                <td className="p-3 text-center text-slate-500">
                                  {field.is_nullable ? 'Yes' : 'No'}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Data Preview Tab */}
                  {activeTab === 'preview' && (
                    <div className="space-y-4">
                      {loadingPreview ? (
                        <div className="flex justify-center items-center py-12 flex-col space-y-2">
                          <div className="h-8 w-8 rounded-full border-2 border-sky-500 border-t-transparent animate-spin"></div>
                          <span className="text-xs text-slate-400">Loading preview data...</span>
                        </div>
                      ) : !previewData || previewData.rows.length === 0 ? (
                        <div className="text-center p-8 border border-dashed border-[#1e293b] rounded-xl text-slate-500 text-xs">
                          No preview rows returned from this database table or api.
                        </div>
                      ) : (
                        <div className="border border-[#1e293b] rounded-xl overflow-x-auto bg-[#070b13]/20">
                          <table className="w-full text-left border-collapse text-xs">
                            <thead>
                              <tr className="border-b border-[#1e293b] bg-slate-900/60 text-slate-400 font-bold uppercase tracking-wider">
                                {previewData.columns.map((col) => (
                                  <th key={col} className="p-3 font-mono">{col}</th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {previewData.rows.map((row, rIdx) => (
                                <tr key={rIdx} className="border-b border-[#1e293b]/50 hover:bg-slate-800/10 text-slate-300">
                                  {row.map((cell, cIdx) => {
                                    const displayValue = cell === null || cell === undefined
                                      ? 'null'
                                      : typeof cell === 'object'
                                      ? JSON.stringify(cell)
                                      : String(cell);
                                    return (
                                      <td key={cIdx} className="p-3 text-slate-300 whitespace-nowrap" title={displayValue}>
                                        {cell === null || cell === undefined ? (
                                          <span className="text-slate-600">null</span>
                                        ) : typeof cell === 'object' ? (
                                          <span className="font-mono text-teal-400 bg-teal-950/20 px-1.5 py-0.5 rounded border border-teal-500/10 text-[10px]">{displayValue}</span>
                                        ) : (
                                          displayValue
                                        )}
                                      </td>
                                    );
                                  })}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Cross-Entity Relations Tab */}
                  {activeTab === 'relationships' && (
                    <div className="space-y-6">
                      {/* Create New Link Form */}
                      <form onSubmit={handleCreateRelationship} className="bg-[#070b13]/40 border border-[#1e293b] p-4 rounded-xl space-y-4">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-white flex items-center space-x-1">
                          <Plus className="h-4 w-4 text-sky-400" />
                          <span>Link Relationship</span>
                        </h4>
                        
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                          {/* Source Field */}
                          <div className="space-y-1">
                            <label className="text-[10px] uppercase font-bold text-slate-400">Source Column</label>
                            <select
                              value={sourceField}
                              onChange={(e) => setSourceField(e.target.value)}
                              required
                              className="bg-[#070b13] border border-slate-800 text-xs text-slate-300 px-2.5 py-1.5 rounded-lg w-full focus:outline-none focus:border-sky-500"
                            >
                              <option value="">-- Select --</option>
                              {selectedEntity.fields.map((f: any) => (
                                <option key={f.id} value={f.id}>{f.display_name}</option>
                              ))}
                            </select>
                          </div>

                          {/* Cardinality */}
                          <div className="space-y-1">
                            <label className="text-[10px] uppercase font-bold text-slate-400">Cardinality</label>
                            <select
                              value={cardinality}
                              onChange={(e) => setCardinality(e.target.value)}
                              required
                              className="bg-[#070b13] border border-slate-800 text-xs text-slate-300 px-2.5 py-1.5 rounded-lg w-full focus:outline-none focus:border-sky-500"
                            >
                              <option value="one_to_one">One to One (1:1)</option>
                              <option value="one_to_many">One to Many (1:N)</option>
                              <option value="many_to_one">Many to One (N:1)</option>
                            </select>
                          </div>

                          {/* Target Entity */}
                          <div className="space-y-1">
                            <label className="text-[10px] uppercase font-bold text-slate-400">Target Table</label>
                            <select
                              value={targetEntity}
                              onChange={(e) => setTargetEntity(e.target.value)}
                              required
                              className="bg-[#070b13] border border-slate-800 text-xs text-slate-300 px-2.5 py-1.5 rounded-lg w-full focus:outline-none focus:border-sky-500"
                            >
                              <option value="">-- Select --</option>
                              {entities.filter(e => e.id !== selectedEntity.id).map((e) => (
                                <option key={e.id} value={e.id}>{e.display_name}</option>
                              ))}
                            </select>
                          </div>

                          {/* Target Field */}
                          <div className="space-y-1">
                            <label className="text-[10px] uppercase font-bold text-slate-400">Target Column</label>
                            <select
                              value={targetField}
                              onChange={(e) => setTargetField(e.target.value)}
                              required
                              disabled={!targetEntity}
                              className="bg-[#070b13] border border-slate-800 text-xs text-slate-300 px-2.5 py-1.5 rounded-lg w-full focus:outline-none focus:border-sky-500"
                            >
                              <option value="">-- Select --</option>
                              {getTargetFields().map((f: any) => (
                                <option key={f.id} value={f.id}>{f.display_name}</option>
                              ))}
                            </select>
                          </div>
                        </div>

                        <div className="flex justify-end pt-2 border-t border-[#1e293b]/60">
                          <button
                            type="submit"
                            className="bg-[#1e293b] hover:bg-sky-500/20 text-white hover:text-sky-400 border border-slate-700 hover:border-sky-500/30 px-4 py-1.5 rounded-lg text-xs font-bold transition-all"
                          >
                            Add Relationship Link
                          </button>
                        </div>
                      </form>

                      {/* Display Relationships */}
                      <div className="space-y-3">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1">
                          <Layers className="h-3.5 w-3.5 text-teal-400" />
                          <span>Linked Relationships</span>
                        </h4>

                        {relationships.length === 0 ? (
                          <div className="text-center p-6 border border-dashed border-[#1e293b] rounded-xl text-slate-500 text-xs">
                            No logical cross-table relations configured for this data source yet.
                          </div>
                        ) : (
                          <div className="space-y-2">
                            {relationships.map((rel) => (
                              <div key={rel.id} className="p-3 border border-[#1e293b] bg-[#070b13]/20 rounded-xl flex items-center justify-between text-xs">
                                <div className="flex items-center space-x-2.5">
                                  <span className="font-bold text-white">{getEntityDisplayName(rel.source_entity_id)}</span>
                                  <span className="font-mono text-sky-400">({getFieldDisplayName(rel.source_entity_id, rel.source_field_id)})</span>
                                  
                                  <span className="text-[10px] bg-slate-800 text-slate-300 font-bold px-2 py-0.5 rounded-full uppercase">
                                    {rel.cardinality.replace(/_/g, ' ')}
                                  </span>
                                  
                                  <span className="font-bold text-white">{getEntityDisplayName(rel.target_entity_id)}</span>
                                  <span className="font-mono text-teal-400">({getFieldDisplayName(rel.target_entity_id, rel.target_field_id)})</span>
                                </div>

                                <button
                                  onClick={() => handleDeleteRelationship(rel.id)}
                                  className="text-rose-500 hover:text-rose-400 p-1.5 rounded-lg hover:bg-rose-500/10 transition-all cursor-pointer"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="flex-1 flex flex-col justify-center items-center text-center text-slate-500 space-y-2">
                <Info className="h-8 w-8 text-slate-600" />
                <p className="text-sm font-semibold">Select a Catalog Entity</p>
                <p className="text-xs text-slate-600">Choose a table/endpoint from the sidebar list to inspect properties.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
