import { create } from 'zustand';

// Extend base API helper to support ports 8002 and 8005 specifically
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

async function connectorServiceRequest(path: string, options: any = {}) {
  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  const token = localStorage.getItem('discover_token');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  options.headers = headers;

  const response = await fetch(`http://localhost:8005/api/v1${path}`, options);
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Connector Service Error' }));
    throw new Error(err.detail || 'Connector Service Error');
  }
  return response.json();
}

export interface MetadataEntity {
  id: number;
  entity_key: string;
  entity_type: string;
  name: string;
  description?: string;
  attributes: Record<string, string>;
  details: Array<{
    field_name: string;
    display_name: string;
    category: string;
    data_type: string;
    value: string;
  }>;
}

export interface MetadataField {
  id: number;
  name: string;
  display_name: string;
  data_type: string;
  description?: string;
  category: string;
  is_required: boolean;
}

export interface MetadataRelationship {
  id: number;
  datasource_id: number;
  source_entity_key: string;
  source_field_name: string;
  target_entity_key: string;
  target_field_name: string;
  cardinality: string;
}

export interface MetadataVersion {
  id: number;
  datasource_id: number;
  version: number;
  snapshot_data: string;
  changes_detected?: string;
  created_at: string;
}

export interface MetadataSyncHistory {
  id: number;
  datasource_id: number;
  datasource_name: string;
  status: string;
  started_at: string;
  completed_at: string;
  records_synced: number;
  error_message?: string;
  changes_detected?: string;
}

interface MetadataState {
  entities: MetadataEntity[];
  fields: MetadataField[];
  relationships: MetadataRelationship[];
  syncHistory: MetadataSyncHistory[];
  versions: Record<number, MetadataVersion[]>;
  dataSources: any[];
  loading: boolean;
  syncingSourceId: number | null;

  fetchMetadata: () => Promise<void>;
  fetchRelationships: () => Promise<void>;
  fetchSyncHistory: () => Promise<void>;
  fetchVersions: (datasourceId: number) => Promise<void>;
  fetchDataSources: () => Promise<void>;
  syncDatasource: (datasourceId: number) => Promise<void>;
}

export const useMetadataStore = create<MetadataState>((set, get) => ({
  entities: [],
  fields: [],
  relationships: [],
  syncHistory: [],
  versions: {},
  dataSources: [],
  loading: false,
  syncingSourceId: null,

  fetchMetadata: async () => {
    set({ loading: true });
    try {
      const entities = await metadataServiceRequest('/metadata/entities');
      const fields = await metadataServiceRequest('/metadata/fields');
      set({ entities, fields, loading: false });
    } catch (err) {
      console.error('Failed to fetch metadata entities/fields:', err);
      set({ loading: false });
    }
  },

  fetchRelationships: async () => {
    try {
      const relationships = await metadataServiceRequest('/metadata/federation/relationships');
      set({ relationships });
    } catch (err) {
      console.error('Failed to fetch relationships:', err);
    }
  },

  fetchSyncHistory: async () => {
    try {
      const syncHistory = await metadataServiceRequest('/metadata/federation/history');
      set({ syncHistory });
    } catch (err) {
      console.error('Failed to fetch sync history:', err);
    }
  },

  fetchVersions: async (datasourceId: number) => {
    try {
      const data = await metadataServiceRequest(`/metadata/federation/versions/${datasourceId}`);
      set((state) => ({
        versions: {
          ...state.versions,
          [datasourceId]: data
        }
      }));
    } catch (err) {
      console.error(`Failed to fetch version history for source ${datasourceId}:`, err);
    }
  },

  fetchDataSources: async () => {
    try {
      const dataSources = await connectorServiceRequest('/connectors/sources');
      set({ dataSources });
    } catch (err) {
      console.error('Failed to fetch data sources:', err);
    }
  },

  syncDatasource: async (datasourceId: number) => {
    set({ syncingSourceId: datasourceId });
    try {
      // Trigger sync in Connector Service (port 8005)
      await connectorServiceRequest(`/connectors/sources/${datasourceId}/sync`, { method: 'POST' });
      
      // Re-fetch all data to propagate the changes immediately
      await get().fetchMetadata();
      await get().fetchRelationships();
      await get().fetchSyncHistory();
      await get().fetchVersions(datasourceId);
    } catch (err) {
      console.error(`Failed to sync source ${datasourceId}:`, err);
    } finally {
      set({ syncingSourceId: null });
    }
  }
}));
