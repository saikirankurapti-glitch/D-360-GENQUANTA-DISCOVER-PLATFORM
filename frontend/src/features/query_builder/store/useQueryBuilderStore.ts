import { create } from 'zustand';
import { applyNodeChanges, applyEdgeChanges, addEdge } from '@xyflow/react';
import type { Node, Edge, OnNodesChange, OnEdgesChange, OnConnect, Connection } from '@xyflow/react';
import { compileGraphToSQL } from '../utils/sqlCompiler';
import { validateQueryGraph } from '../utils/queryValidator';

// Extend base API helper to support port 8003 specifically
async function queryServiceRequest(path: string, options: any = {}) {
  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  const token = localStorage.getItem('discover_token');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  options.headers = headers;

  const response = await fetch(`http://localhost:8003/api/v1${path}`, options);
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Query Service Error' }));
    throw new Error(err.detail || 'Query Service Error');
  }
  return response.json();
}

async function metadataServiceRequest(path: string, options: any = {}) {
  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  const token = localStorage.getItem('discover_token');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  options.headers = headers;

  const response = await fetch(`http://localhost:8002/api/v1${path}`, options);
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Metadata Service Error' }));
    throw new Error(err.detail || 'Metadata Service Error');
  }
  return response.json();
}

export type NodeData = {
  entityType: string;
  physicalTableName?: string;
  selectedFields: string[];
  filters: Array<{ field: string; operator: string; value: string }>;
  [key: string]: any;
};

export type EdgeData = {
  joinCondition?: string;
  [key: string]: any;
};

interface QueryBuilderState {
  nodes: Node<NodeData>[];
  edges: Edge<EdgeData>[];
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  compiledSQL: string;
  validationErrors: string[];
  templates: any[];
  metadataEntities: any[];
  metadataFields: any[];
  metadataRelationships: any[];
  loading: boolean;

  setNodes: (nodes: Node<NodeData>[]) => void;
  setEdges: (edges: Edge<EdgeData>[]) => void;
  onNodesChange: OnNodesChange<Node<NodeData>>;
  onEdgesChange: OnEdgesChange<Edge<EdgeData>>;
  onConnect: OnConnect;
  
  addEntityNode: (entityType: string, physicalTableName?: string) => void;
  updateNodeData: (nodeId: string, updates: Partial<NodeData>) => void;
  updateEdgeData: (edgeId: string, updates: Partial<EdgeData>) => void;
  selectNode: (nodeId: string | null) => void;
  selectEdge: (edgeId: string | null) => void;
  deleteNode: (nodeId: string) => void;
  deleteEdge: (edgeId: string) => void;
  
  runCompilationAndValidation: () => void;
  fetchMetadataEntities: () => Promise<void>;
  fetchTemplates: () => Promise<void>;
  saveTemplate: (name: string, description?: string) => Promise<void>;
  duplicateTemplate: (id: number) => Promise<void>;
  loadTemplate: (template: any) => void;
  clearCanvas: () => void;
}

export const useQueryBuilderStore = create<QueryBuilderState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  selectedEdgeId: null,
  compiledSQL: '',
  validationErrors: [],
  templates: [],
  metadataEntities: [],
  metadataFields: [],
  metadataRelationships: [],
  loading: false,

  setNodes: (nodes) => {
    set({ nodes });
    get().runCompilationAndValidation();
  },

  setEdges: (edges) => {
    set({ edges });
    get().runCompilationAndValidation();
  },

  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes)
    });
    get().runCompilationAndValidation();
  },

  onEdgesChange: (changes) => {
    set({
      edges: applyEdgeChanges(changes, get().edges)
    });
    get().runCompilationAndValidation();
  },

  onConnect: (connection: Connection) => {
    const currentEdges = get().edges;
    const edgeData: EdgeData = {
      joinCondition: ''
    };
    
    const newEdges = addEdge({ ...connection, data: edgeData, type: 'smoothstep' }, currentEdges);
    set({ edges: newEdges });
    get().runCompilationAndValidation();
  },

  addEntityNode: (entityType, physicalTableName) => {
    const id = `${entityType.toLowerCase().replace(/[^a-z0-9]/g, '_')}-${Date.now()}`;
    
    // Find schema columns from metadata entities
    const matchedEntity = get().metadataEntities.find(
      e => e.entity_key === entityType || e.name === entityType
    );
    
    let defaultFields: string[] = [];
    if (matchedEntity && matchedEntity.details) {
      defaultFields = matchedEntity.details.map((d: any) => d.display_name).slice(0, 3);
    } else {
      defaultFields = entityType.toLowerCase() === 'compound' 
        ? ['entity_key', 'name', 'mw'] 
        : ['entity_key', 'name', 'ic50_nm'];
    }

    const newNode: Node<NodeData> = {
      id,
      type: 'entityNode',
      position: { x: 100 + get().nodes.length * 60, y: 100 + get().nodes.length * 60 },
      data: {
        entityType,
        physicalTableName: physicalTableName || entityType,
        selectedFields: defaultFields,
        filters: []
      }
    };
    set({
      nodes: [...get().nodes, newNode],
      selectedNodeId: id,
      selectedEdgeId: null
    });
    get().runCompilationAndValidation();
  },

  updateNodeData: (nodeId, updates) => {
    set({
      nodes: get().nodes.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: { ...node.data, ...updates }
          };
        }
        return node;
      })
    });
    get().runCompilationAndValidation();
  },

  updateEdgeData: (edgeId, updates) => {
    set({
      edges: get().edges.map((edge) => {
        if (edge.id === edgeId) {
          return {
            ...edge,
            data: { ...edge.data, ...updates }
          };
        }
        return edge;
      })
    });
    get().runCompilationAndValidation();
  },

  selectNode: (nodeId) => {
    set({ selectedNodeId: nodeId, selectedEdgeId: null });
  },

  selectEdge: (edgeId) => {
    set({ selectedEdgeId: edgeId, selectedNodeId: null });
  },

  deleteNode: (nodeId) => {
    set({
      nodes: get().nodes.filter((node) => node.id !== nodeId),
      edges: get().edges.filter((edge) => edge.source !== nodeId && edge.target !== nodeId),
      selectedNodeId: get().selectedNodeId === nodeId ? null : get().selectedNodeId
    });
    get().runCompilationAndValidation();
  },

  deleteEdge: (edgeId) => {
    set({
      edges: get().edges.filter((edge) => edge.id !== edgeId),
      selectedEdgeId: get().selectedEdgeId === edgeId ? null : get().selectedEdgeId
    });
    get().runCompilationAndValidation();
  },

  runCompilationAndValidation: () => {
    const { nodes, edges } = get();
    const errors = validateQueryGraph(nodes, edges);
    const sql = compileGraphToSQL(nodes, edges);
    
    set({
      validationErrors: errors,
      compiledSQL: errors.length === 0 ? sql : ''
    });
  },

  fetchMetadataEntities: async () => {
    try {
      const entities = await metadataServiceRequest('/metadata/entities');
      const fields = await metadataServiceRequest('/metadata/fields');
      const relationships = await metadataServiceRequest('/metadata/federation/relationships');
      set({ 
        metadataEntities: entities, 
        metadataFields: fields,
        metadataRelationships: relationships 
      });
    } catch (err) {
      console.error('Failed to load metadata in Query Builder:', err);
    }
  },

  fetchTemplates: async () => {
    set({ loading: true });
    try {
      const data = await queryServiceRequest('/query/templates');
      set({ templates: data });
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      set({ loading: false });
    }
  },

  saveTemplate: async (name, description = '') => {
    const { nodes, edges, compiledSQL } = get();
    try {
      const payload = {
        name,
        description,
        layout_json: JSON.stringify({ nodes, edges }),
        sql_preview: compiledSQL,
        created_by: localStorage.getItem('discover_email') || 'system'
      };
      await queryServiceRequest('/query/templates', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      await get().fetchTemplates();
    } catch (error) {
      console.error('Failed to save template:', error);
      throw error;
    }
  },

  duplicateTemplate: async (id) => {
    try {
      await queryServiceRequest(`/query/templates/${id}/duplicate`, {
        method: 'POST'
      });
      await get().fetchTemplates();
    } catch (error) {
      console.error('Failed to duplicate template:', error);
    }
  },

  loadTemplate: (template) => {
    try {
      const layout = JSON.parse(template.layout_json);
      set({
        nodes: layout.nodes || [],
        edges: layout.edges || [],
        selectedNodeId: null,
        selectedEdgeId: null
      });
      get().runCompilationAndValidation();
    } catch (error) {
      console.error('Failed to load template layout:', error);
    }
  },

  clearCanvas: () => {
    set({
      nodes: [],
      edges: [],
      selectedNodeId: null,
      selectedEdgeId: null,
      compiledSQL: '',
      validationErrors: []
    });
  }
}));
