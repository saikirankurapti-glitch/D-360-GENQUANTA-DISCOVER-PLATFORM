import type { Node, Edge } from '@xyflow/react';
import type { NodeData, EdgeData } from '../store/useQueryBuilderStore';
import { useQueryBuilderStore } from '../store/useQueryBuilderStore';

export function compileGraphToSQL(nodes: Node<NodeData>[], edges: Edge<EdgeData>[]): string {
  if (nodes.length === 0) return '';

  const selectFields: string[] = [];
  const joins: string[] = [];
  const whereClauses: string[] = [];
  
  // Retrieve active relationships from metadata store
  const metadataRelationships = useQueryBuilderStore.getState().metadataRelationships || [];

  // Map nodes by id for quick lookup
  const nodeMap = new Map<string, {
    id: string;
    entityType: string;
    tableName: string;
    alias: string;
    selectedFields: string[];
    filters: any[];
  }>();

  nodes.forEach((node) => {
    const entityType = node.data?.entityType || 'Compound';
    
    // Resolve dynamic physical table name
    let tableName = `${entityType.toLowerCase()}s`;
    if (entityType.toLowerCase() !== 'compound' && entityType.toLowerCase() !== 'assay') {
      tableName = node.data?.physicalTableName || entityType;
      // Strip datasource prefix for local DuckDB schema resolving if needed, e.g. postgres.public.compounds -> compounds
      if (tableName.includes('.')) {
        const parts = tableName.split('.');
        tableName = parts[parts.length - 1];
      }
    }
    
    const alias = `${entityType.toLowerCase().replace(/[^a-z0-9]/g, '_')}_${node.id.replace(/-/g, '_').substring(0, 8)}`;
    
    nodeMap.set(node.id, {
      id: node.id,
      entityType,
      tableName,
      alias,
      selectedFields: node.data?.selectedFields || [],
      filters: node.data?.filters || [],
    });
  });

  const firstNodeId = nodes[0].id;
  const firstNode = nodeMap.get(firstNodeId)!;
  const fromTable = `${firstNode.tableName} AS ${firstNode.alias}`;

  // Process select fields for primary node
  if (firstNode.selectedFields.length > 0) {
    firstNode.selectedFields.forEach((field) => {
      selectFields.push(`${firstNode.alias}.${field}`);
    });
  } else {
    selectFields.push(`${firstNode.alias}.*`);
  }

  // Process filters for primary node
  firstNode.filters.forEach((filter) => {
    const { field, operator, value } = filter;
    if (!field || value === undefined || value === '') return;

    if (operator.toLowerCase() === 'between') {
      whereClauses.push(`${firstNode.alias}.${field} BETWEEN ${value}`);
    } else {
      const isNumeric = !isNaN(Number(value)) && value.trim() !== '';
      if (isNumeric) {
        whereClauses.push(`${firstNode.alias}.${field} ${operator} ${value}`);
      } else {
        whereClauses.push(`${firstNode.alias}.${field} ${operator} '${value}'`);
      }
    }
  });

  const joinedNodes = new Set<string>([firstNodeId]);

  // Process edges (joins)
  edges.forEach((edge) => {
    const sourceId = edge.source;
    const targetId = edge.target;

    if (!nodeMap.has(sourceId) || !nodeMap.has(targetId)) return;

    const sourceNode = nodeMap.get(sourceId)!;
    const targetNode = nodeMap.get(targetId)!;

    let nodeToJoin: typeof targetNode | null = null;
    let anchorNode: typeof sourceNode | null = null;

    if (!joinedNodes.has(targetId)) {
      nodeToJoin = targetNode;
      anchorNode = sourceNode;
      joinedNodes.add(targetId);
    } else if (!joinedNodes.has(sourceId)) {
      nodeToJoin = sourceNode;
      anchorNode = targetNode;
      joinedNodes.add(sourceId);
    }

    if (nodeToJoin && anchorNode) {
      // Dynamic relationship key resolution
      const rel = metadataRelationships.find(r => 
        (r.source_entity_key.toLowerCase() === anchorNode!.entityType.toLowerCase() && 
         r.target_entity_key.toLowerCase() === nodeToJoin!.entityType.toLowerCase()) ||
        (r.source_entity_key.toLowerCase() === nodeToJoin!.entityType.toLowerCase() && 
         r.target_entity_key.toLowerCase() === anchorNode!.entityType.toLowerCase())
      );

      let joinColAnchor = '';
      let joinColJoin = '';

      if (rel) {
        if (rel.source_entity_key.toLowerCase() === anchorNode.entityType.toLowerCase()) {
          joinColAnchor = rel.source_field_name;
          joinColJoin = rel.target_field_name;
        } else {
          joinColAnchor = rel.target_field_name;
          joinColJoin = rel.source_field_name;
        }
      } else {
        // Fallback heuristics
        joinColAnchor = anchorNode.entityType.toLowerCase() === 'compound' ? 'id' : 'compound_id';
        joinColJoin = nodeToJoin.entityType.toLowerCase() === 'compound' ? 'id' : 'compound_id';
      }

      // Assemble INNER JOIN syntax
      joins.push(
        `INNER JOIN ${nodeToJoin.tableName} AS ${nodeToJoin.alias} ON ${anchorNode.alias}.${joinColAnchor} = ${nodeToJoin.alias}.${joinColJoin}`
      );

      // Selected fields
      if (nodeToJoin.selectedFields.length > 0) {
        nodeToJoin.selectedFields.forEach((field) => {
          selectFields.push(`${nodeToJoin!.alias}.${field}`);
        });
      } else {
        selectFields.push(`${nodeToJoin.alias}.*`);
      }

      // Filters
      nodeToJoin.filters.forEach((filter) => {
        const { field, operator, value } = filter;
        if (!field || value === undefined || value === '') return;

        if (operator.toLowerCase() === 'between') {
          whereClauses.push(`${nodeToJoin!.alias}.${field} BETWEEN ${value}`);
        } else {
          const isNumeric = !isNaN(Number(value)) && value.trim() !== '';
          if (isNumeric) {
            whereClauses.push(`${nodeToJoin!.alias}.${field} ${operator} ${value}`);
          } else {
            whereClauses.push(`${nodeToJoin!.alias}.${field} ${operator} '${value}'`);
          }
        }
      });
    }
  });

  let sql = `SELECT ${selectFields.join(', ')}\nFROM ${fromTable}`;
  
  if (joins.length > 0) {
    sql += `\n${joins.join('\n')}`;
  }
  
  if (whereClauses.length > 0) {
    sql += `\nWHERE ${whereClauses.join(' AND ')}`;
  }

  return sql;
}
