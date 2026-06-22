import { Handle, Position } from '@xyflow/react';
import type { NodeProps, Node } from '@xyflow/react';
import { useQueryBuilderStore } from '../store/useQueryBuilderStore';
import type { NodeData } from '../store/useQueryBuilderStore';
import { FlaskConical, Microscope, Trash2 } from 'lucide-react';

export const EntityNode = ({ id, data, selected }: NodeProps<Node<NodeData>>) => {
  const { deleteNode, selectNode } = useQueryBuilderStore();
  const nodeData = data;
  const isCompound = nodeData.entityType === 'Compound';

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    deleteNode(id);
  };

  return (
    <div
      onClick={() => selectNode(id)}
      className={`w-56 bg-[#0c1220] border-2 rounded-xl overflow-hidden shadow-2xl transition-all ${
        selected
          ? 'border-sky-500 shadow-[0_0_20px_rgba(14,165,233,0.25)]'
          : 'border-slate-800 hover:border-slate-700'
      }`}
    >
      {/* Node Header */}
      <div
        className={`px-4 py-3 flex items-center justify-between border-b ${
          isCompound
            ? 'bg-sky-500/10 border-sky-500/20 text-sky-400'
            : 'bg-teal-500/10 border-teal-500/20 text-teal-400'
        }`}
      >
        <div className="flex items-center space-x-2">
          {isCompound ? (
            <FlaskConical className="h-4 w-4" />
          ) : (
            <Microscope className="h-4 w-4" />
          )}
          <span className="font-bold text-sm tracking-wider uppercase">
            {nodeData.entityType}
          </span>
        </div>
        <button
          onClick={handleDelete}
          className="text-slate-500 hover:text-rose-400 p-0.5 rounded transition-colors"
          title="Delete Node"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      {/* Selected columns checklist summary */}
      <div className="p-3 space-y-2 bg-[#070b13]/80">
        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wide">
          Projections ({nodeData.selectedFields?.length || 0})
        </p>
        <div className="space-y-1">
          {nodeData.selectedFields && nodeData.selectedFields.length > 0 ? (
            nodeData.selectedFields.map((f) => (
              <div
                key={f}
                className="text-xs font-mono text-slate-300 bg-slate-900/40 border border-slate-950 px-2 py-0.5 rounded flex items-center"
              >
                <div className="h-1.5 w-1.5 rounded-full bg-emerald-400 mr-2"></div>
                <span className="truncate">{f}</span>
              </div>
            ))
          ) : (
            <span className="text-xs text-slate-600 italic">None selected</span>
          )}
        </div>

        {/* Filters preview */}
        {nodeData.filters && nodeData.filters.length > 0 && (
          <div className="pt-2 border-t border-slate-900">
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wide">
              Filters ({nodeData.filters.length})
            </p>
            <div className="space-y-1 mt-1">
              {nodeData.filters.map((flt, i) => (
                <span
                  key={i}
                  className="inline-block text-[9px] bg-rose-500/10 border border-rose-500/20 text-rose-400 px-1.5 py-0.5 rounded"
                >
                  {flt.field} {flt.operator} {flt.value}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* React Flow handles for wiring connections */}
      {/* Target handle on left */}
      <Handle
        type="target"
        position={Position.Left}
        id="handle-left"
        className="!w-3 !h-3 !bg-slate-800 hover:!bg-sky-500 !border-slate-700 transition-colors"
      />

      {/* Source handle on right */}
      <Handle
        type="source"
        position={Position.Right}
        id="handle-right"
        className="!w-3 !h-3 !bg-slate-800 hover:!bg-sky-500 !border-slate-700 transition-colors"
      />
    </div>
  );
};
