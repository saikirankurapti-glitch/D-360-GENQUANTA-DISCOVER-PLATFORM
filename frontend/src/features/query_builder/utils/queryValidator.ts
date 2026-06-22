import type { Node, Edge } from '@xyflow/react';
import type { NodeData, EdgeData } from '../store/useQueryBuilderStore';

export function validateQueryGraph(nodes: Node<NodeData>[], edges: Edge<EdgeData>[]): string[] {
  const errors: string[] = [];

  if (nodes.length === 0) {
    return errors;
  }

  // 1. Verify Connectivity (BFS to check if all nodes are reachable in an undirected graph representation)
  const adjacencyList = new Map<string, string[]>();
  nodes.forEach((node) => adjacencyList.set(node.id, []));

  edges.forEach((edge) => {
    const u = edge.source;
    const v = edge.target;
    if (adjacencyList.has(u) && adjacencyList.has(v)) {
      adjacencyList.get(u)!.push(v);
      adjacencyList.get(v)!.push(u);
    }
  });

  const visited = new Set<string>();
  const queue: string[] = [nodes[0].id];
  visited.add(nodes[0].id);

  while (queue.length > 0) {
    const current = queue.shift()!;
    const neighbors = adjacencyList.get(current) || [];
    neighbors.forEach((neighbor) => {
      if (!visited.has(neighbor)) {
        visited.add(neighbor);
        queue.push(neighbor);
      }
    });
  }

  if (visited.size < nodes.length) {
    errors.push('Disconnected components found. All query entity nodes must be connected.');
  }

  // 2. Validate node-specific settings
  nodes.forEach((node) => {
    if (!node.data?.selectedFields || node.data.selectedFields.length === 0) {
      errors.push(`Entity node "${node.id}" has no projection columns selected.`);
    }

    // Verify filter completeness
    node.data?.filters?.forEach((filter) => {
      if (!filter.field) {
        errors.push(`Empty filter field configured on node "${node.id}".`);
      }
      if (filter.value === undefined || filter.value.trim() === '') {
        errors.push(`Empty filter value for field "${filter.field}" on node "${node.id}".`);
      }
    });
  });

  return errors;
}
