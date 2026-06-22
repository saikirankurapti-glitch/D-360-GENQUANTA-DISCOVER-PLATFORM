import { create } from 'zustand';
import { chemistryService } from '../services/chemistryService';
import type { 
  ChemicalSearchResult, 
  MolecularDescriptors, 
  CompoundActivityInput, 
  SARResponseData 
} from '../services/chemistryService';

interface SearchHistoryItem {
  id: string;
  smiles: string;
  type: 'exact' | 'substructure' | 'similarity';
  threshold: number;
  timestamp: string;
}

interface CompoundStoreState {
  // Search state
  searchSmiles: string;
  searchType: 'exact' | 'substructure' | 'similarity';
  similarityThreshold: number;
  searchResults: ChemicalSearchResult[];
  selectedSearchResult: ChemicalSearchResult | null;
  selectedDescriptors: MolecularDescriptors | null;
  searchHistory: SearchHistoryItem[];
  loading: boolean;
  error: string | null;

  // SAR state
  sarScaffold: string;
  sarCompoundsInput: CompoundActivityInput[];
  sarDecomposition: SARResponseData | null;
  sarLoading: boolean;
  sarError: string | null;

  // Search actions
  setSearchSmiles: (smiles: string) => void;
  setSearchType: (type: 'exact' | 'substructure' | 'similarity') => void;
  setSimilarityThreshold: (threshold: number) => void;
  executeSearch: () => Promise<void>;
  selectResult: (result: ChemicalSearchResult | null) => Promise<void>;
  clearSearch: () => void;
  loadHistoryItem: (item: SearchHistoryItem) => void;
  clearHistory: () => void;

  // SAR actions
  setSARScaffold: (smiles: string) => void;
  setSARCompoundsInput: (compounds: CompoundActivityInput[]) => void;
  addSARCompound: (compound: CompoundActivityInput) => void;
  removeSARCompound: (index: number) => void;
  runSARDecomposition: () => Promise<void>;
  clearSAR: () => void;
}

// Load initial history from localStorage
const getLocalHistory = (): SearchHistoryItem[] => {
  try {
    const data = localStorage.getItem('discover_chemistry_history');
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
};

export const useCompoundStore = create<CompoundStoreState>((set, get) => ({
  // Search state
  searchSmiles: '',
  searchType: 'exact',
  similarityThreshold: 0.7,
  searchResults: [],
  selectedSearchResult: null,
  selectedDescriptors: null,
  searchHistory: getLocalHistory(),
  loading: false,
  error: null,

  // SAR state
  sarScaffold: '',
  sarCompoundsInput: [
    // Pre-populate with seed compounds to match tests for demo purpose
    { smiles: 'Cc1ccccc1', activity: 50.0, name: 'Toluene' },
    { smiles: 'Oc1ccccc1', activity: 1.0, name: 'Phenol' },
    { smiles: 'Clc1ccccc1', activity: 55.0, name: 'Chlorobenzene' },
    { smiles: 'Nc1ccccc1', activity: 100.0, name: 'Aniline' }
  ],
  sarDecomposition: null,
  sarLoading: false,
  sarError: null,

  // Search actions
  setSearchSmiles: (smiles) => set({ searchSmiles: smiles }),
  setSearchType: (type) => set({ searchType: type }),
  setSimilarityThreshold: (threshold) => set({ similarityThreshold: threshold }),
  
  executeSearch: async () => {
    const { searchSmiles, searchType, similarityThreshold, searchHistory } = get();
    if (!searchSmiles.trim()) return;

    set({ loading: true, error: null, selectedSearchResult: null, selectedDescriptors: null });
    try {
      const results = await chemistryService.search(searchSmiles, searchType, similarityThreshold);
      
      // Add to history
      const newHistoryItem: SearchHistoryItem = {
        id: crypto.randomUUID(),
        smiles: searchSmiles,
        type: searchType,
        threshold: similarityThreshold,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      const updatedHistory = [newHistoryItem, ...searchHistory.slice(0, 19)];
      localStorage.setItem('discover_chemistry_history', JSON.stringify(updatedHistory));

      set({ 
        searchResults: results, 
        searchHistory: updatedHistory,
        loading: false 
      });
    } catch (err: any) {
      console.error('Search failed:', err);
      set({ error: err.message || 'Structure search failed', loading: false });
    }
  },

  selectResult: async (result) => {
    if (!result) {
      set({ selectedSearchResult: null, selectedDescriptors: null });
      return;
    }

    set({ selectedSearchResult: result, selectedDescriptors: null });
    try {
      const descriptors = await chemistryService.getDescriptors(result.smiles);
      set({ selectedDescriptors: descriptors });
    } catch (err) {
      console.error('Failed to load properties:', err);
    }
  },

  clearSearch: () => {
    set({
      searchSmiles: '',
      searchResults: [],
      selectedSearchResult: null,
      selectedDescriptors: null,
      error: null
    });
  },

  loadHistoryItem: (item) => {
    set({
      searchSmiles: item.smiles,
      searchType: item.type,
      similarityThreshold: item.threshold
    });
    get().executeSearch();
  },

  clearHistory: () => {
    localStorage.removeItem('discover_chemistry_history');
    set({ searchHistory: [] });
  },

  // SAR actions
  setSARScaffold: (smiles) => set({ sarScaffold: smiles }),
  setSARCompoundsInput: (compounds) => set({ sarCompoundsInput: compounds }),
  
  addSARCompound: (compound) => {
    set({
      sarCompoundsInput: [...get().sarCompoundsInput, compound]
    });
  },
  
  removeSARCompound: (index) => {
    set({
      sarCompoundsInput: get().sarCompoundsInput.filter((_, i) => i !== index)
    });
  },

  runSARDecomposition: async () => {
    const { sarScaffold, sarCompoundsInput } = get();
    if (!sarScaffold.trim()) {
      set({ sarError: 'Scaffold structure is required' });
      return;
    }
    if (sarCompoundsInput.length === 0) {
      set({ sarError: 'Analogues list cannot be empty' });
      return;
    }

    set({ sarLoading: true, sarError: null, sarDecomposition: null });
    try {
      const decomp = await chemistryService.performSAR(sarScaffold, sarCompoundsInput);
      set({ sarDecomposition: decomp, sarLoading: false });
    } catch (err: any) {
      console.error('SAR analysis failed:', err);
      set({ sarError: err.message || 'SAR decomposition failed', sarLoading: false });
    }
  },

  clearSAR: () => {
    set({
      sarScaffold: '',
      sarDecomposition: null,
      sarError: null
    });
  }
}));
