import { apiRequest } from '../../../services/api';

export interface ChemicalSearchResult {
  id: number;
  entity_key: string;
  name: string;
  smiles: string;
  similarity?: number;
}

export interface MolecularDescriptors {
  smiles: string;
  mw: number;
  logp: number;
  tpsa: number;
  hbd: number;
  hba: number;
  rotatable_bonds: number;
  formula: string;
  heavy_atoms: number;
}

export interface CompoundActivityInput {
  smiles: string;
  activity: number;
  name?: string;
}

export interface SARAnalogueResult {
  name: string;
  smiles: string;
  activity: number;
  core_smiles: string;
  r_groups: Record<string, string>;
}

export interface SARCliff {
  compound_a: string;
  compound_b: string;
  differing_r_group: string;
  group_a: string;
  group_b: string;
  activity_a: number;
  activity_b: number;
  activity_ratio: number;
}

export interface SARResponseData {
  scaffold: string;
  compounds: SARAnalogueResult[];
  activity_cliffs: SARCliff[];
}

export const chemistryService = {
  /**
   * Search database for compounds matching structure query
   */
  async search(
    smiles: string,
    type: 'exact' | 'substructure' | 'similarity' = 'exact',
    threshold = 0.7,
    limit = 100
  ): Promise<ChemicalSearchResult[]> {
    const params = new URLSearchParams({
      smiles,
      type,
      threshold: String(threshold),
      limit: String(limit),
    });
    return apiRequest(`/search?${params.toString()}`, {
      service: 'chemistry',
      method: 'GET',
    });
  },

  /**
   * Retrieve physical properties/descriptors of a structure
   */
  async getDescriptors(smiles: string): Promise<MolecularDescriptors> {
    const params = new URLSearchParams({ smiles });
    return apiRequest(`/descriptors?${params.toString()}`, {
      service: 'chemistry',
      method: 'GET',
    });
  },

  /**
   * Perform Structure-Activity Relationship (SAR) analysis
   */
  async performSAR(
    scaffoldSmiles: string,
    compounds: CompoundActivityInput[]
  ): Promise<SARResponseData> {
    return apiRequest('/sar', {
      service: 'chemistry',
      method: 'POST',
      body: JSON.stringify({
        scaffold_smiles: scaffoldSmiles,
        compounds: compounds.map((c) => ({
          smiles: c.smiles,
          activity: Number(c.activity),
          name: c.name || undefined,
        })),
      }),
    });
  },
};
