import { useQueryBuilderStore } from '../store/useQueryBuilderStore';
import { Settings, Plus, Trash2, Sliders, Link as LinkIcon, Database } from 'lucide-react';

export const ConfigPanel = () => {
  const {
    nodes,
    edges,
    selectedNodeId,
    selectedEdgeId,
    updateNodeData,
    metadataEntities
  } = useQueryBuilderStore();

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);
  const selectedEdge = edges.find((e) => e.id === selectedEdgeId);

  // Field Options based on Entity Type
  const compoundFields = [
    { name: 'entity_key', label: 'Entity Key' },
    { name: 'name', label: 'Name' },
    { name: 'mw', label: 'Molecular Weight (mw)' },
    { name: 'clogp', label: 'cLogP' },
    { name: 'smiles', label: 'SMILES' },
  ];

  const assayFields = [
    { name: 'entity_key', label: 'Entity Key' },
    { name: 'name', label: 'Name' },
    { name: 'ic50_nm', label: 'IC50 (nM)' },
    { name: 'target_protein', label: 'Target Protein' },
  ];

  const getFieldsForNode = (): Array<{ name: string; label: string }> => {
    if (!selectedNode) return [];
    const type = selectedNode.data.entityType;
    if (type === 'Compound') return compoundFields;
    if (type === 'Assay') return assayFields;

    // Look up dynamic fields from synced metadata entities
    const matched = metadataEntities.find(e => e.entity_key === type || e.name === type);
    if (matched && matched.details) {
      return matched.details.map((d: any) => ({
        name: d.display_name,
        label: d.display_name
      }));
    }
    return [];
  };

  const handleFieldToggle = (fieldName: string) => {
    if (!selectedNode) return;
    const currentFields = selectedNode.data.selectedFields || [];
    const updatedFields = currentFields.includes(fieldName)
      ? currentFields.filter((f) => f !== fieldName)
      : [...currentFields, fieldName];
    
    updateNodeData(selectedNode.id, { selectedFields: updatedFields });
  };

  const handleAddFilter = () => {
    if (!selectedNode) return;
    const currentFilters = selectedNode.data.filters || [];
    const fields = getFieldsForNode();
    const newFilter = {
      field: fields[0]?.name || 'entity_key',
      operator: '=',
      value: '',
    };
    
    updateNodeData(selectedNode.id, { filters: [...currentFilters, newFilter] });
  };

  const handleRemoveFilter = (index: number) => {
    if (!selectedNode) return;
    const currentFilters = selectedNode.data.filters || [];
    updateNodeData(selectedNode.id, {
      filters: currentFilters.filter((_, idx) => idx !== index),
    });
  };

  const handleFilterChange = (index: number, key: string, val: string) => {
    if (!selectedNode) return;
    const currentFilters = [...(selectedNode.data.filters || [])];
    currentFilters[index] = { ...currentFilters[index], [key]: val };
    updateNodeData(selectedNode.id, { filters: currentFilters });
  };

  if (selectedNode) {
    const isCompound = selectedNode.data.entityType === 'Compound';
    const fields = getFieldsForNode();
    const selectedFields = selectedNode.data.selectedFields || [];
    const filters = selectedNode.data.filters || [];

    return (
      <div className="glass-panel border border-slate-800 rounded-2xl p-6 h-full overflow-y-auto space-y-6">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-4">
          <Settings className="h-5 w-5 text-sky-400" />
          <h3 className="font-bold text-white text-sm">Node Configuration</h3>
        </div>

        <div className="space-y-1">
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Entity Details</p>
          <div className="bg-[#070b13] border border-slate-900 rounded-xl p-3 flex justify-between items-center">
            <div>
              <p className="text-xs font-semibold text-slate-300 capitalize">{selectedNode.data.entityType}</p>
              <p className="text-[9px] font-mono text-slate-500">{selectedNode.id}</p>
            </div>
            <span className={`text-[9px] px-2 py-0.5 rounded font-bold uppercase border ${
              isCompound ? 'bg-sky-500/10 text-sky-400 border-sky-500/20' : 'bg-teal-500/10 text-teal-400 border-teal-500/20'
            }`}>
              {isCompound ? 'Chemical' : 'Biological'}
            </span>
          </div>
        </div>

        {/* Selected Fields Checkbox List */}
        <div className="space-y-3">
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider flex items-center">
            <Database className="h-3.5 w-3.5 text-sky-400 mr-1.5" />
            <span>Select Output Columns</span>
          </p>
          <div className="bg-[#070b13] border border-slate-900 rounded-xl p-3.5 space-y-2">
            {fields.map((f) => (
              <label key={f.name} className="flex items-center space-x-3 text-xs text-slate-300 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={selectedFields.includes(f.name)}
                  onChange={() => handleFieldToggle(f.name)}
                  className="rounded border-slate-800 text-sky-500 bg-[#0d1322] focus:ring-sky-500/20"
                />
                <span className="font-mono">{f.name}</span>
                <span className="text-[10px] text-slate-500">({f.label})</span>
              </label>
            ))}
          </div>
        </div>

        {/* Filters Panel */}
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider flex items-center">
              <Sliders className="h-3.5 w-3.5 text-teal-400 mr-1.5" />
              <span>Query Filters</span>
            </p>
            <button
              onClick={handleAddFilter}
              className="flex items-center space-x-1 bg-sky-500 hover:bg-sky-600 text-white text-[10px] font-bold px-2.5 py-1 rounded-lg transition-colors cursor-pointer"
            >
              <Plus className="h-3 w-3" />
              <span>Add</span>
            </button>
          </div>

          <div className="space-y-3">
            {filters.length === 0 ? (
              <p className="text-xs text-slate-500 italic text-center py-4 bg-[#070b13] border border-slate-900 border-dashed rounded-xl">
                No filters defined for this entity
              </p>
            ) : (
              filters.map((filter, index) => (
                <div key={index} className="bg-[#070b13] border border-slate-900 rounded-xl p-3.5 space-y-2.5 relative">
                  <button
                    onClick={() => handleRemoveFilter(index)}
                    className="absolute top-2 right-2 text-slate-600 hover:text-rose-400 p-0.5 rounded transition-colors"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>

                  <div>
                    <label className="block text-[9px] font-bold text-slate-500 uppercase mb-1">Column</label>
                    <select
                      value={filter.field}
                      onChange={(e) => handleFilterChange(index, 'field', e.target.value)}
                      className="w-full bg-[#0d1322] border border-slate-800 text-xs text-slate-300 py-1.5 px-2 rounded-lg focus:border-sky-500 focus:outline-none"
                    >
                      {fields.map((f) => (
                        <option key={f.name} value={f.name}>
                          {f.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-[9px] font-bold text-slate-500 uppercase mb-1">Op</label>
                      <select
                        value={filter.operator}
                        onChange={(e) => handleFilterChange(index, 'operator', e.target.value)}
                        className="w-full bg-[#0d1322] border border-slate-800 text-xs text-slate-300 py-1.5 px-2 rounded-lg focus:border-sky-500 focus:outline-none"
                      >
                        <option value="=">=</option>
                        <option value=">">&gt;</option>
                        <option value="<">&lt;</option>
                        <option value=">=">&gt;=</option>
                        <option value="<=">&lt;=</option>
                        <option value="LIKE">LIKE</option>
                        <option value="BETWEEN">BETWEEN</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[9px] font-bold text-slate-500 uppercase mb-1">Value</label>
                      <input
                        type="text"
                        value={filter.value}
                        onChange={(e) => handleFilterChange(index, 'value', e.target.value)}
                        placeholder={filter.operator === 'BETWEEN' ? '10 AND 50' : 'Value'}
                        className="w-full bg-[#0d1322] border border-slate-800 text-xs text-slate-300 py-1.5 px-2 rounded-lg focus:border-sky-500 focus:outline-none"
                      />
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    );
  }

  if (selectedEdge) {
    return (
      <div className="glass-panel border border-slate-800 rounded-2xl p-6 h-full overflow-y-auto space-y-6">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-4">
          <LinkIcon className="h-5 w-5 text-teal-400" />
          <h3 className="font-bold text-white text-sm">Join Configuration</h3>
        </div>

        <div className="space-y-4">
          <div className="bg-[#070b13] border border-slate-900 rounded-xl p-3">
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">Relationship</p>
            <p className="text-xs font-semibold text-slate-300">{selectedEdge.source} ⇄ {selectedEdge.target}</p>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Join Constraint Type</label>
            <select
              value="inner"
              disabled
              className="w-full bg-[#0d1322] border border-slate-800 text-xs text-slate-400 py-2.5 px-3 rounded-lg focus:outline-none opacity-60"
            >
              <option value="inner">INNER JOIN (Standard PK/FK)</option>
            </select>
          </div>

          <div className="bg-sky-500/5 border border-sky-500/10 p-4 rounded-xl">
            <p className="text-xs text-sky-400 font-semibold mb-1">Inferred Key Join</p>
            <p className="text-[10px] text-slate-400 leading-relaxed">
              GenQuantaa automatically compiles join constraints by referencing mapping keys (e.g. <code>Compound.id = Assay.compound_id</code>).
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-panel border border-slate-800 rounded-2xl p-6 h-full flex flex-col justify-center items-center text-center text-slate-500">
      <Sliders className="h-10 w-10 text-slate-700 mb-2.5" />
      <p className="text-sm font-semibold text-slate-400">No Node Selected</p>
      <p className="text-xs text-slate-600 max-w-xs mt-1">
        Select a node or a connection on the canvas to configure projection columns, conditions, or join properties.
      </p>
    </div>
  );
};
