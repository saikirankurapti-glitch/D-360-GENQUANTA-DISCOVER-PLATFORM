import { useMemo } from 'react';
import { ReactFlow, Background, Controls, MiniMap } from '@xyflow/react';
import type { NodeTypes } from '@xyflow/react';
import { useQueryBuilderStore } from '../store/useQueryBuilderStore';
import { EntityNode } from './EntityNode';
import '@xyflow/react/dist/style.css';

export const QueryCanvas = () => {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    selectNode,
    selectEdge
  } = useQueryBuilderStore();

  const nodeTypes = useMemo<NodeTypes>(() => ({
    entityNode: EntityNode,
  }), []);

  return (
    <div className="h-full w-full bg-[#070b13] rounded-2xl border border-slate-800 overflow-hidden relative shadow-[0_4px_30px_rgba(0,0,0,0.5)]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        onPaneClick={() => {
          selectNode(null);
          selectEdge(null);
        }}
        onEdgeClick={(_, edge) => {
          selectEdge(edge.id);
        }}
      >
        <Background color="#1e293b" gap={16} size={1} />
        <Controls className="!bg-[#0c1220] !border-slate-800 !text-slate-300" />
        <MiniMap
          nodeStrokeColor={(n) => (n.type === 'entityNode' ? '#0ea5e9' : '#334155')}
          nodeColor={(n) => (n.type === 'entityNode' ? '#0c1220' : '#1e293b')}
          className="!bg-[#0c1220] !border-slate-800"
          maskColor="rgba(7, 11, 19, 0.7)"
        />
      </ReactFlow>
      
      {/* Help Overlay */}
      <div className="absolute top-4 left-4 bg-[#0c1220]/90 border border-slate-800 px-4 py-2.5 rounded-xl text-[10px] text-slate-400 max-w-xs space-y-1 pointer-events-none backdrop-blur">
        <p className="font-bold text-white uppercase tracking-wider">Canvas Operations</p>
        <p>• Click sidebar buttons to insert entity nodes.</p>
        <p>• Drag handles between nodes to configure joins.</p>
        <p>• Select nodes to edit filters and projections.</p>
      </div>
    </div>
  );
};
