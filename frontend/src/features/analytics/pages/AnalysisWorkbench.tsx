import { useEffect, useState, useMemo } from 'react';
import { apiRequest } from '../../../services/api';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import _createPlotlyComponent from 'react-plotly.js/factory';
import Plotly from 'plotly.js-dist-min';

const createPlotlyComponent = typeof _createPlotlyComponent === 'function'
  ? _createPlotlyComponent
  : (_createPlotlyComponent as any).default;

const Plot = createPlotlyComponent(Plotly);
import { 
  BarChart4, Database, Save, FolderOpen, RefreshCw, 
  Settings, HelpCircle, Activity, Sparkles, Trash2, CheckCircle2,
  Maximize2, Minimize2, Download, Filter, Sliders, ChevronDown, 
  Trash, ArrowLeft, Info, Table, BarChart2
} from 'lucide-react';

// Demo Dataset for instant wow-factor testing
const DEMO_COLUMNS = ["compound_key", "mw", "logp", "tpsa", "hba", "hbd", "concentration_um", "inhibition_pct", "cell_viability_pct", "outcome"];
const DEMO_ROWS = [
  // Dose response curves for 6 concentrations of Compound A
  ["CHEM-A-001", 380.12, 2.45, 75.4, 5, 2, 0.001, 2.5, 98.4, "Inactive"],
  ["CHEM-A-001", 380.12, 2.45, 75.4, 5, 2, 0.01, 8.2, 97.2, "Inactive"],
  ["CHEM-A-001", 380.12, 2.45, 75.4, 5, 2, 0.1, 28.4, 96.5, "Inactive"],
  ["CHEM-A-001", 380.12, 2.45, 75.4, 5, 2, 1.0, 56.1, 95.8, "Active"],
  ["CHEM-A-001", 380.12, 2.45, 75.4, 5, 2, 10.0, 85.9, 91.2, "Active"],
  ["CHEM-A-001", 380.12, 2.45, 75.4, 5, 2, 100.0, 97.8, 88.4, "Active"],
  
  // Dose response curves for 6 concentrations of Compound B (Highly Active)
  ["CHEM-B-002", 412.35, 3.12, 85.2, 6, 1, 0.001, 12.4, 99.1, "Inactive"],
  ["CHEM-B-002", 412.35, 3.12, 85.2, 6, 1, 0.01, 35.8, 98.4, "Inactive"],
  ["CHEM-B-002", 412.35, 3.12, 85.2, 6, 1, 0.1, 74.2, 94.2, "Active"],
  ["CHEM-B-002", 412.35, 3.12, 85.2, 6, 1, 1.0, 92.5, 90.1, "Active"],
  ["CHEM-B-002", 412.35, 3.12, 85.2, 6, 1, 10.0, 98.4, 86.4, "Active"],
  ["CHEM-B-002", 412.35, 3.12, 85.2, 6, 1, 100.0, 99.8, 72.1, "Active"],

  // More compounds for PCA and clustering
  ["CHEM-C-003", 298.15, 1.85, 45.2, 3, 1, 1.0, 4.2, 99.4, "Inactive"],
  ["CHEM-D-004", 512.45, 4.82, 110.6, 8, 3, 1.0, 48.9, 93.1, "Active"],
  ["CHEM-E-005", 342.22, 2.10, 62.8, 4, 2, 1.0, 89.1, 96.2, "Active"],
  ["CHEM-F-006", 460.18, 3.90, 92.1, 6, 2, 1.0, 91.2, 91.5, "Active"],
  ["CHEM-G-007", 270.08, 0.95, 38.4, 2, 0, 1.0, 1.5, 99.8, "Inactive"],
  ["CHEM-H-008", 325.26, 2.72, 58.1, 4, 1, 1.0, 15.6, 97.4, "Inactive"],
  ["CHEM-I-009", 488.54, 4.15, 102.5, 7, 2, 1.0, 62.4, 92.8, "Active"],
  ["CHEM-J-010", 360.40, 2.95, 71.2, 5, 1, 1.0, 78.5, 94.6, "Active"],
  ["CHEM-K-011", 415.33, 3.48, 80.5, 5, 2, 1.0, 22.8, 98.1, "Inactive"],
  ["CHEM-L-012", 305.10, 1.20, 52.3, 3, 1, 1.0, 8.4, 99.0, "Inactive"],
  ["CHEM-M-013", 530.62, 5.25, 125.4, 9, 3, 1.0, 94.2, 85.1, "Active"],
  ["CHEM-N-014", 395.21, 2.80, 78.9, 5, 1, 1.0, 41.5, 96.4, "Active"]
];

export const AnalysisWorkbench = () => {
  // Navigation & loaders
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [queryHistory, setQueryHistory] = useState<any[]>([]);
  const [savedWorkspaces, setSavedWorkspaces] = useState<any[]>([]);
  const [currentWorkspaceName, setCurrentWorkspaceName] = useState('');
  const [currentWorkspaceDesc, setCurrentWorkspaceDesc] = useState('');
  
  // Loaded dataset state
  const [columns, setColumns] = useState<string[]>([]);
  const [rows, setRows] = useState<any[][]>([]);
  const [selectedHistoryId, setSelectedHistoryId] = useState<string>('');
  
  // Tab states
  const [activeTab, setActiveTab] = useState<'grid' | 'visuals' | 'dimred' | 'clustering' | 'correlation' | 'doseresp'>('grid');

  // Exploratory Visuals configuration
  const [plotType, setPlotType] = useState<string>('scatter');
  const [xCol, setXCol] = useState('');
  const [yCol, setYCol] = useState('');
  const [colorCol, setColorCol] = useState('');
  const [groupByCol, setGroupByCol] = useState('');
  const [aggregation, setAggregation] = useState<string>('None');
  const [sortBy, setSortBy] = useState<string>('none');
  const [sortOrder, setSortOrder] = useState<string>('asc');
  const [activeFilters, setActiveFilters] = useState<Record<string, any>>({});
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [drillDownPath, setDrillDownPath] = useState<string[]>([]);
  const [drillDownFilters, setDrillDownFilters] = useState<Record<string, any>>({});
  const [plotlyRef, setPlotlyRef] = useState<any>(null);

  // PCA / Dimension Reduction state
  const [selectedFeatures, setSelectedFeatures] = useState<string[]>([]);
  const [pcaCoords, setPcaCoords] = useState<any[]>([]);
  const [explainedVar, setExplainedVar] = useState<number[]>([]);
  const [pcaLoadings, setPcaLoadings] = useState<any[]>([]);
  const [pcaLoadingError, setPcaLoadingError] = useState<string | null>(null);
  const [pcaLoading, setPcaLoading] = useState(false);

  // t-SNE / UMAP state
  const [tsneCoords, setTsneCoords] = useState<any[]>([]);
  const [perplexity, setPerplexity] = useState(10);
  const [tsneLoading, setTsneLoading] = useState(false);

  // Clustering state
  const [clusterAlgorithm, setClusterAlgorithm] = useState<'kmeans' | 'dbscan'>('kmeans');
  const [nClusters, setNClusters] = useState(3);
  const [eps, setEps] = useState(0.5);
  const [clusterLabels, setClusterLabels] = useState<number[]>([]);
  const [clusterLoading, setClusterLoading] = useState(false);

  // Correlation state
  const [corrMatrix, setCorrMatrix] = useState<number[][]>([]);
  const [corrColumns, setCorrColumns] = useState<string[]>([]);
  const [corrLoading, setCorrLoading] = useState(false);

  // Dose Response state
  const [doseConcCol, setDoseConcCol] = useState('');
  const [doseRespCol, setDoseRespCol] = useState('');
  const [doseGroupCol, setDoseGroupCol] = useState(''); // Group points by compound name
  const [doseFitResults, setDoseFitResults] = useState<any | null>(null);
  const [doseFitting, setDoseFitting] = useState(false);

  // Fetch initial history
  useEffect(() => {
    loadMetadata();
  }, []);

  const loadMetadata = async () => {
    try {
      setLoadingHistory(true);
      // Load federated query history
      const history = await apiRequest('/query/history', { service: 'query' });
      setQueryHistory(history);

      // Load saved workspaces
      const workspaces = await apiRequest('/analytics/workspaces', { service: 'query' });
      setSavedWorkspaces(workspaces);
    } catch (e) {
      console.error('Failed to load histories:', e);
    } finally {
      setLoadingHistory(false);
    }
  };

  // Run demo dataset instantly
  const loadDemoDataset = () => {
    setColumns(DEMO_COLUMNS);
    setRows(DEMO_ROWS);
    
    // Auto-configure axis variables based on typical schema columns
    setXCol("mw");
    setYCol("logp");
    setColorCol("outcome");
    
    // Auto-select features for reduction
    setSelectedFeatures(["mw", "logp", "tpsa", "hba", "hbd", "cell_viability_pct"]);
    setDoseConcCol("concentration_um");
    setDoseRespCol("inhibition_pct");
    setDoseGroupCol("compound_key");

    // Clear stale fits
    setDoseFitResults(null);
    setPcaCoords([]);
    setTsneCoords([]);
    setClusterLabels([]);
    setCorrMatrix([]);
  };

  // Handle query history selection
  const handleQuerySelect = async (historyIdStr: string) => {
    setSelectedHistoryId(historyIdStr);
    if (!historyIdStr) return;

    try {
      setLoadingHistory(true);
      // Retrieve the historical query
      const histItem = queryHistory.find(h => h.id === Number(historyIdStr));
      if (!histItem || !histItem.sql) return;

      // Execute query fetch via execution route or read cache
      const payload = {
        sql: histItem.sql,
        use_cache: true,
        page: 1,
        page_size: 1000 // Load full dataset for analysis
      };
      
      const response = await apiRequest('/query/execute', {
        service: 'query',
        method: 'POST',
        body: JSON.stringify(payload)
      });

      if (response && response.columns && response.rows) {
        setColumns(response.columns);
        setRows(response.rows);
        
        // Auto select cols
        const numericalCols = getNumericColumns(response.columns, response.rows);
        if (numericalCols.length >= 2) {
          setXCol(numericalCols[0]);
          setYCol(numericalCols[1]);
          setSelectedFeatures(numericalCols);
        }
        
        const categorical = response.columns.find((c: string) => !numericalCols.includes(c));
        if (categorical) setColorCol(categorical);

        setDoseFitResults(null);
        setPcaCoords([]);
        setTsneCoords([]);
        setClusterLabels([]);
        setCorrMatrix([]);
      }
    } catch (err) {
      alert(`Failed to retrieve history query details: ${err}`);
    } finally {
      setLoadingHistory(false);
    }
  };

  // Detect numerical columns
  const getNumericColumns = (cols: string[], dataset: any[][]) => {
    if (dataset.length === 0) return [];
    return cols.filter((_, idx) => {
      // check if first few rows are numeric
      const val = dataset[0][idx];
      return typeof val === 'number' || (!isNaN(Number(val)) && val !== '');
    });
  };

  const numericCols = useMemo(() => getNumericColumns(columns, rows), [columns, rows]);

  // Column profiles computed automatically on columns/rows load
  const columnProfiles = useMemo(() => {
    if (!columns || columns.length === 0 || !rows || rows.length === 0) return [];
    
    return columns.map((colName, colIdx) => {
      const vals = rows.map(r => r[colIdx]).filter(v => v !== null && v !== undefined);
      
      // Determine if numeric
      const isAllNumeric = vals.length > 0 && vals.every(v => {
        if (typeof v === 'number') return true;
        if (typeof v === 'string') {
          const s = v.trim();
          return s !== '' && !isNaN(Number(s));
        }
        return false;
      });
      
      // Determine if date
      const dateRegex = /^\d{4}-\d{2}-\d{2}/;
      const isAllDate = vals.length > 0 && vals.every(v => {
        if (typeof v === 'string') {
          return dateRegex.test(v) || !isNaN(Date.parse(v));
        }
        return false;
      });
      
      const distinctVals = Array.from(new Set(vals));
      const cardinality = distinctVals.length;
      
      let type: 'numeric' | 'categorical' | 'date' | 'id_text' = 'id_text';
      if (isAllNumeric) {
        type = 'numeric';
      } else if (isAllDate) {
        type = 'date';
      } else if (cardinality <= 25 || cardinality < vals.length * 0.4) {
        type = 'categorical';
      }
      
      let min, max, sum, mean;
      if (type === 'numeric') {
        const numVals = vals.map(v => Number(v));
        min = Math.min(...numVals);
        max = Math.max(...numVals);
        sum = numVals.reduce((acc, curr) => acc + (isNaN(curr) ? 0 : curr), 0);
        mean = sum / numVals.length;
      }
      
      return {
        name: colName,
        type,
        cardinality,
        distinctValues: distinctVals,
        min,
        max,
        sum,
        mean
      };
    });
  }, [columns, rows]);

  // Recommendations derived dynamically from column profiles
  const chartRecommendations = useMemo(() => {
    const recommendations: Array<{
      title: string;
      chartType: string;
      xCol: string;
      yCol: string;
      groupByCol?: string;
      colorByCol?: string;
      aggregation?: string;
      reason: string;
    }> = [];
    
    const numerics = columnProfiles.filter(p => p.type === 'numeric');
    const categoricals = columnProfiles.filter(p => p.type === 'categorical');
    const dates = columnProfiles.filter(p => p.type === 'date');
    
    // 1. Numeric vs Numeric -> Scatter Plot
    if (numerics.length >= 2) {
      recommendations.push({
        title: `Scatter: ${numerics[0].name} vs ${numerics[1].name}`,
        chartType: 'scatter',
        xCol: numerics[0].name,
        yCol: numerics[1].name,
        colorByCol: categoricals.length > 0 ? categoricals[0].name : '',
        reason: 'Plot continuous parameters to inspect outliers and correlation.'
      });
    }
    
    // 2. Category vs Numeric -> Bar Chart
    if (categoricals.length > 0 && numerics.length > 0) {
      recommendations.push({
        title: `Avg ${numerics[0].name} by ${categoricals[0].name}`,
        chartType: 'bar',
        xCol: categoricals[0].name,
        yCol: numerics[0].name,
        aggregation: 'Avg',
        reason: 'Compare key metric averages across discrete cohorts.'
      });
    }
    
    // 3. Date vs Numeric -> Line Chart
    if (dates.length > 0 && numerics.length > 0) {
      recommendations.push({
        title: `TimeSeries of ${numerics[0].name}`,
        chartType: 'timeseries',
        xCol: dates[0].name,
        yCol: numerics[0].name,
        reason: 'Plot chronological values sequentially to reveal time-based trends.'
      });
    }
    
    // 4. Single Numeric -> Histogram / Box Plot
    if (numerics.length > 0) {
      recommendations.push({
        title: `Distribution of ${numerics[0].name}`,
        chartType: 'distribution',
        xCol: numerics[0].name,
        yCol: '',
        reason: 'Evaluate density distribution curve & shape profile.'
      });
      
      recommendations.push({
        title: `BoxPlot of ${numerics[0].name}`,
        chartType: 'box',
        xCol: categoricals.length > 0 ? categoricals[0].name : '',
        yCol: numerics[0].name,
        reason: 'Display interquartile range (IQR), median and data spread.'
      });
    }
    
    // 5. Multiple Numerics -> Correlation Heatmap
    if (numerics.length >= 3) {
      recommendations.push({
        title: 'Correlation Heatmap',
        chartType: 'correlation_heatmap',
        xCol: '',
        yCol: '',
        reason: 'Generate cross-correlation matrix across all continuous parameters.'
      });
    }
    
    // 6. Hierarchical -> Treemap
    if (categoricals.length >= 2) {
      recommendations.push({
        title: `Treemap: ${categoricals[0].name} & ${categoricals[1].name}`,
        chartType: 'treemap',
        xCol: categoricals[0].name,
        yCol: categoricals[1].name,
        reason: 'Inspect nested category ratios and hierarchical tree sizes.'
      });
    }
    
    // 7. Pie chart composition
    if (categoricals.length > 0) {
      recommendations.push({
        title: `${categoricals[0].name} Share Composition`,
        chartType: 'pie',
        xCol: categoricals[0].name,
        yCol: '',
        reason: 'Understand component ratios for low-cardinality divisions.'
      });
    }
    
    return recommendations;
  }, [columnProfiles]);

  // Dynamically filter rows based on active filters
  const filteredRows = useMemo(() => {
    return rows.filter(row => {
      // 1. Apply user active filters
      for (const colName of Object.keys(activeFilters)) {
        const colIdx = columns.indexOf(colName);
        if (colIdx === -1) continue;
        const val = row[colIdx];
        const filterVal = activeFilters[colName];
        
        const profile = columnProfiles.find(p => p.name === colName);
        if (!profile) continue;
        
        if (profile.type === 'numeric') {
          const num = Number(val);
          if (filterVal.min !== undefined && num < filterVal.min) return false;
          if (filterVal.max !== undefined && num > filterVal.max) return false;
        } else {
          // Categorical filter
          if (filterVal && filterVal.length > 0 && !filterVal.includes(val)) {
            return false;
          }
        }
      }
      
      // 2. Apply drilldown filters
      for (const colName of Object.keys(drillDownFilters)) {
        const colIdx = columns.indexOf(colName);
        if (colIdx === -1) continue;
        const val = row[colIdx];
        if (String(val) !== String(drillDownFilters[colName])) return false;
      }
      
      return true;
    });
  }, [rows, columns, activeFilters, drillDownFilters, columnProfiles]);

  const handleChartClick = (clickedVal: any) => {
    const categoricals = columnProfiles.filter(p => p.type === 'categorical' && p.name !== xCol);
    
    if (['bar', 'horizontal_bar', 'stacked_bar', 'pie', 'donut', 'treemap'].includes(plotType) && categoricals.length > 0 && xCol) {
      setDrillDownFilters(prev => ({ ...prev, [xCol]: clickedVal }));
      setDrillDownPath(prev => [...prev, `${xCol}: ${clickedVal}`]);
      setXCol(categoricals[0].name);
    } else if (xCol) {
      const currentFilter = activeFilters[xCol] || [];
      const isSelected = currentFilter.includes(clickedVal);
      const newFilter = isSelected 
        ? currentFilter.filter((v: any) => v !== clickedVal)
        : [...currentFilter, clickedVal];
        
      setActiveFilters(prev => ({
        ...prev,
        [xCol]: newFilter.length > 0 ? newFilter : undefined
      }));
    }
  };

  const handleDrillUp = () => {
    if (drillDownPath.length === 0) return;
    const lastPath = drillDownPath[drillDownPath.length - 1];
    const originalCol = lastPath.split(':')[0];
    
    setDrillDownFilters(prev => {
      const copy = { ...prev };
      delete copy[originalCol];
      return copy;
    });
    setDrillDownPath(prev => prev.slice(0, -1));
    setXCol(originalCol);
  };

  const getAggregatedTraces = () => {
    if (filteredRows.length === 0 || !xCol) return [];
    const xIdx = columns.indexOf(xCol);
    const yIdx = yCol ? columns.indexOf(yCol) : -1;
    const groupIdx = groupByCol ? columns.indexOf(groupByCol) : -1;
    
    const groups: Record<string, Record<string, any[]>> = {};
    
    filteredRows.forEach(row => {
      const xVal = String(row[xIdx] !== null && row[xIdx] !== undefined ? row[xIdx] : 'Null');
      const groupVal = groupIdx !== -1 ? String(row[groupIdx] !== null && row[groupIdx] !== undefined ? row[groupIdx] : 'All') : 'All';
      const yVal = yIdx !== -1 ? Number(row[yIdx]) : 1;
      
      if (!groups[groupVal]) groups[groupVal] = {};
      if (!groups[groupVal][xVal]) groups[groupVal][xVal] = [];
      groups[groupVal][xVal].push(yVal);
    });
    
    const uniqueX = Array.from(new Set(filteredRows.map(row => String(row[xIdx] !== null && row[xIdx] !== undefined ? row[xIdx] : 'Null'))));
    
    return Object.keys(groups).map(groupName => {
      const xValues: string[] = [];
      const yValues: number[] = [];
      
      uniqueX.forEach(xVal => {
        const vals = groups[groupName][xVal];
        if (!vals || vals.length === 0) {
          xValues.push(xVal);
          yValues.push(0);
          return;
        }
        
        let aggVal = 0;
        const count = vals.length;
        const sum = vals.reduce((a, b) => a + (isNaN(b) ? 0 : b), 0);
        const avg = sum / count;
        const min = Math.min(...vals.filter(v => !isNaN(v)));
        const max = Math.max(...vals.filter(v => !isNaN(v)));
        
        if (aggregation === 'Sum') aggVal = sum;
        else if (aggregation === 'Avg') aggVal = avg;
        else if (aggregation === 'Min') aggVal = isFinite(min) ? min : 0;
        else if (aggregation === 'Max') aggVal = isFinite(max) ? max : 0;
        else aggVal = count; // Count
        
        xValues.push(xVal);
        yValues.push(aggVal);
      });
      
      if (sortBy === 'x') {
        const indices = Array.from(xValues.keys());
        indices.sort((a, b) => {
          const valA = xValues[a];
          const valB = xValues[b];
          const numA = Number(valA);
          const numB = Number(valB);
          if (!isNaN(numA) && !isNaN(numB)) {
            return sortOrder === 'asc' ? numA - numB : numB - numA;
          }
          return sortOrder === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
        });
        return {
          groupName,
          x: indices.map(i => xValues[i]),
          y: indices.map(i => yValues[i])
        };
      } else if (sortBy === 'y') {
        const indices = Array.from(yValues.keys());
        indices.sort((a, b) => sortOrder === 'asc' ? yValues[a] - yValues[b] : yValues[b] - yValues[a]);
        return {
          groupName,
          x: indices.map(i => xValues[i]),
          y: indices.map(i => yValues[i])
        };
      }
      
      return {
        groupName,
        x: xValues,
        y: yValues
      };
    });
  };

  const plotlyData = useMemo(() => {
    if (filteredRows.length === 0) return [];

    const xIdx = columns.indexOf(xCol);
    const yIdx = columns.indexOf(yCol);
    const colorIdx = colorCol ? columns.indexOf(colorCol) : -1;

    const rawX = filteredRows.map(r => r[xIdx]);
    const rawY = yCol ? filteredRows.map(r => r[yIdx]) : [];

    switch (plotType) {
      case 'scatter': {
        if (!xCol || !yCol) return [];
        if (colorIdx !== -1) {
          const uniqueColors = Array.from(new Set(filteredRows.map(r => r[colorIdx])));
          return uniqueColors.map(colorVal => {
            const subRows = filteredRows.filter(r => r[colorIdx] === colorVal);
            return {
              x: subRows.map(r => r[xIdx]),
              y: subRows.map(r => r[yIdx]),
              mode: 'markers',
              type: 'scatter',
              name: String(colorVal),
              marker: { size: 9 }
            };
          });
        }
        return [{
          x: rawX,
          y: rawY,
          mode: 'markers',
          type: 'scatter',
          name: 'Datapoints',
          marker: { color: '#0ea5e9', size: 9 }
        }];
      }

      case 'bubble': {
        if (!xCol || !yCol) return [];
        const sizeVals = rawY.map(v => Math.max(5, Math.min(50, Number(v) * 0.1 || 10)));
        return [{
          x: rawX,
          y: rawY,
          mode: 'markers',
          type: 'scatter',
          name: 'Bubbles',
          marker: {
            color: '#10b981',
            size: sizeVals,
            sizemode: 'area',
            sizeref: 0.1
          }
        }];
      }

      case 'histogram': {
        if (!xCol) return [];
        return [{
          x: rawX,
          type: 'histogram',
          marker: { color: '#0ea5e9', opacity: 0.7 }
        }];
      }

      case 'box': {
        if (!yCol) return [];
        return [{
          x: xCol ? rawX : undefined,
          y: rawY,
          type: 'box',
          marker: { color: '#14b8a6' }
        }];
      }

      case 'violin': {
        if (!yCol) return [];
        return [{
          x: xCol ? rawX : undefined,
          y: rawY,
          type: 'violin',
          box: { visible: true },
          meanline: { visible: true },
          line: { color: '#8b5cf6' }
        }];
      }

      case 'correlation_heatmap': {
        const numerics = columnProfiles.filter(p => p.type === 'numeric').map(p => p.name);
        if (numerics.length < 2) return [];
        
        const matrix: number[][] = [];
        numerics.forEach((rowCol) => {
          const rowVals = filteredRows.map(r => Number(r[columns.indexOf(rowCol)]));
          const rowCorr: number[] = [];
          numerics.forEach((colCol) => {
            const colVals = filteredRows.map(r => Number(r[columns.indexOf(colCol)]));
            
            const meanRow = rowVals.reduce((a, b) => a + b, 0) / rowVals.length;
            const meanCol = colVals.reduce((a, b) => a + b, 0) / colVals.length;
            
            let num = 0;
            let denRow = 0;
            let denCol = 0;
            for (let i = 0; i < rowVals.length; i++) {
              const diffRow = rowVals[i] - meanRow;
              const diffCol = colVals[i] - meanCol;
              num += diffRow * diffCol;
              denRow += diffRow * diffRow;
              denCol += diffCol * diffCol;
            }
            const den = Math.sqrt(denRow) * Math.sqrt(denCol);
            const corr = den !== 0 ? num / den : 0;
            rowCorr.push(corr);
          });
          matrix.push(rowCorr);
        });

        return [{
          z: matrix,
          x: numerics,
          y: numerics,
          type: 'heatmap',
          colorscale: 'RdBu',
          zmin: -1,
          zmax: 1
        }];
      }

      case 'heatmap': {
        if (!xCol || !yCol) return [];
        return [{
          x: rawX,
          y: rawY,
          type: 'histogram2d',
          colorscale: 'Viridis'
        }];
      }

      case 'treemap': {
        if (!xCol) return [];
        const traces = getAggregatedTraces();
        if (traces.length === 0) return [];
        const firstTrace = traces[0];
        return [{
          type: 'treemap',
          labels: firstTrace.x,
          parents: firstTrace.x.map(() => ''),
          values: firstTrace.y
        }];
      }

      case 'waterfall': {
        if (!xCol || !yCol) return [];
        const traces = getAggregatedTraces();
        if (traces.length === 0) return [];
        const t = traces[0];
        return [{
          type: 'waterfall',
          x: t.x,
          y: t.y,
          connector: { line: { color: 'rgb(63, 63, 63)' } }
        }];
      }

      case 'timeseries': {
        if (!xCol || !yCol) return [];
        const traces = getAggregatedTraces();
        return traces.map(t => ({
          x: t.x,
          y: t.y,
          type: 'scatter',
          mode: 'lines+markers',
          name: t.groupName,
          line: { shape: 'spline' }
        }));
      }

      case 'distribution': {
        if (!xCol) return [];
        return [
          {
            x: rawX,
            type: 'histogram',
            name: 'Histogram Density',
            opacity: 0.6,
            marker: { color: '#3b82f6' }
          }
        ];
      }

      case 'kpi_cards': {
        if (!yCol) return [];
        const traces = getAggregatedTraces();
        if (traces.length === 0) return [];
        const val = traces[0].y[0] || 0;
        return [{
          type: 'indicator',
          mode: 'number',
          value: val,
          number: { font: { size: 40, color: '#38bdf8' } }
        }];
      }

      default: {
        if (!xCol) return [];
        const traces = getAggregatedTraces();

        if (plotType === 'pie' || plotType === 'donut') {
          const combinedX: string[] = [];
          const combinedY: number[] = [];
          traces.forEach(t => {
            t.x.forEach((xVal, idx) => {
              combinedX.push(`${t.groupName !== 'All' ? t.groupName + ' - ' : ''}${xVal}`);
              combinedY.push(t.y[idx]);
            });
          });
          return [{
            labels: combinedX,
            values: combinedY,
            type: 'pie',
            hole: plotType === 'donut' ? 0.45 : 0
          }];
        }

        if (plotType === 'horizontal_bar') {
          return traces.map(t => ({
            x: t.y,
            y: t.x,
            type: 'bar',
            orientation: 'h',
            name: t.groupName
          }));
        }

        if (plotType === 'area') {
          return traces.map(t => ({
            x: t.x,
            y: t.y,
            type: 'scatter',
            mode: 'lines',
            fill: 'tozeroy',
            name: t.groupName
          }));
        }

        if (plotType === 'line') {
          return traces.map(t => ({
            x: t.x,
            y: t.y,
            type: 'scatter',
            mode: 'lines+markers',
            name: t.groupName
          }));
        }

        return traces.map(t => ({
          x: t.x,
          y: t.y,
          type: 'bar',
          name: t.groupName
        }));
      }
    }
  }, [plotType, xCol, yCol, colorCol, groupByCol, aggregation, sortBy, sortOrder, filteredRows, columns, columnProfiles]);

  const summaryStats = useMemo(() => {
    if (filteredRows.length === 0 || !yCol) return null;
    const yIdx = columns.indexOf(yCol);
    if (yIdx === -1) return null;
    
    const vals = filteredRows.map(r => Number(r[yIdx])).filter(v => !isNaN(v));
    if (vals.length === 0) return null;
    
    const count = vals.length;
    const sum = vals.reduce((a, b) => a + b, 0);
    const avg = sum / count;
    const min = Math.min(...vals);
    const max = Math.max(...vals);
    
    const variance = vals.reduce((a, b) => a + Math.pow(b - avg, 2), 0) / count;
    const stdDev = Math.sqrt(variance);
    
    const sorted = [...vals].sort((a, b) => a - b);
    const median = sorted[Math.floor(count / 2)];
    
    return {
      count,
      sum,
      avg,
      min,
      max,
      stdDev,
      median
    };
  }, [filteredRows, yCol, columns]);

  const exportPNG = () => {
    if (plotlyRef) {
      Plotly.downloadImage(plotlyRef, { format: 'png', width: 1200, height: 800, filename: `plot_${plotType}` });
    }
  };

  const exportSVG = () => {
    if (plotlyRef) {
      Plotly.downloadImage(plotlyRef, { format: 'svg', width: 1200, height: 800, filename: `plot_${plotType}` });
    }
  };

  // PCA calculation
  const executePCA = async () => {
    if (selectedFeatures.length < 2) {
      alert("Please select at least 2 numerical features for PCA.");
      return;
    }
    try {
      setPcaLoading(true);
      setPcaLoadingError(null);
      const res = await apiRequest('/analytics/pca', {
        service: 'query',
        method: 'POST',
        body: JSON.stringify({
          rows,
          columns,
          features: selectedFeatures
        })
      });
      setPcaCoords(res.coords);
      setExplainedVar(res.explained_variance);
      setPcaLoadings(res.loadings);
    } catch (e: any) {
      setPcaLoadingError(e.message || "PCA calculation failed");
    } finally {
      setPcaLoading(false);
    }
  };

  // t-SNE calculation
  const executeTSNE = async () => {
    if (selectedFeatures.length < 2) {
      alert("Please select at least 2 numerical features for t-SNE.");
      return;
    }
    if (rows.length < 5) {
      alert("At least 5 data points are required to run t-SNE.");
      return;
    }
    try {
      setTsneLoading(true);
      const res = await apiRequest('/analytics/tsne', {
        service: 'query',
        method: 'POST',
        body: JSON.stringify({
          rows,
          columns,
          features: selectedFeatures,
          perplexity
        })
      });
      setTsneCoords(res.coords);
    } catch (e: any) {
      alert(`t-SNE computation error: ${e.message}`);
    } finally {
      setTsneLoading(false);
    }
  };

  // Clustering calculation
  const executeClustering = async () => {
    if (selectedFeatures.length < 2) {
      alert("Please select at least 2 numerical features for clustering.");
      return;
    }
    try {
      setClusterLoading(true);
      const res = await apiRequest('/analytics/clustering', {
        service: 'query',
        method: 'POST',
        body: JSON.stringify({
          rows,
          columns,
          features: selectedFeatures,
          algorithm: clusterAlgorithm,
          n_clusters: nClusters,
          eps,
          min_samples: 3
        })
      });
      setClusterLabels(res.labels);
    } catch (e: any) {
      alert(`Clustering computation error: ${e.message}`);
    } finally {
      setClusterLoading(false);
    }
  };

  // Correlation Matrix calculation
  const executeCorrelation = async () => {
    if (numericCols.length < 2) {
      alert("At least 2 numerical columns are required for correlation calculation.");
      return;
    }
    try {
      setCorrLoading(true);
      const res = await apiRequest('/analytics/correlation', {
        service: 'query',
        method: 'POST',
        body: JSON.stringify({
          rows,
          columns,
          features: numericCols
        })
      });
      setCorrMatrix(res.matrix);
      setCorrColumns(res.columns);
    } catch (e: any) {
      alert(`Correlation computation error: ${e.message}`);
    } finally {
      setCorrLoading(false);
    }
  };

  // Dose Response Fit
  const executeDoseResponseFit = async () => {
    if (!doseConcCol || !doseRespCol) {
      alert("Please select concentration and response columns.");
      return;
    }

    try {
      setDoseFitting(true);
      
      const concIdx = columns.indexOf(doseConcCol);
      const respIdx = columns.indexOf(doseRespCol);

      // Extract concentrations and responses
      const concentrations = rows.map(r => Number(r[concIdx]));
      const responses = rows.map(r => Number(r[respIdx]));

      const res = await apiRequest('/analytics/dose-response', {
        service: 'query',
        method: 'POST',
        body: JSON.stringify({ concentrations, responses })
      });

      if (!res.success) {
        alert(`Fitting error: ${res.error}`);
        setDoseFitResults(null);
      } else {
        setDoseFitResults(res);
      }
    } catch (e: any) {
      alert(`Dose response calculation failed: ${e.message}`);
    } finally {
      setDoseFitting(false);
    }
  };

  // Save Analysis Workspace
  const handleSaveWorkspace = async () => {
    if (!currentWorkspaceName.trim()) {
      alert("Please enter a workspace name.");
      return;
    }

    const configs = {
      plotType,
      xCol,
      yCol,
      colorCol,
      selectedFeatures,
      perplexity,
      clusterAlgorithm,
      nClusters,
      eps,
      doseConcCol,
      doseRespCol,
      doseGroupCol
    };

    const payload = {
      name: currentWorkspaceName,
      description: currentWorkspaceDesc,
      query_history_id: selectedHistoryId ? Number(selectedHistoryId) : null,
      dataset_json: JSON.stringify({ columns, rows }),
      configs_json: JSON.stringify(configs)
    };

    try {
      await apiRequest('/analytics/workspaces', {
        service: 'query',
        method: 'POST',
        body: JSON.stringify(payload)
      });
      alert("Analysis Workspace saved successfully!");
      setCurrentWorkspaceName('');
      setCurrentWorkspaceDesc('');
      loadMetadata();
    } catch (e: any) {
      alert(`Save failed: ${e.message}`);
    }
  };

  // Load Analysis Workspace
  const handleLoadWorkspace = (ws: any) => {
    try {
      if (ws.dataset_json) {
        const dataset = JSON.parse(ws.dataset_json);
        setColumns(dataset.columns);
        setRows(dataset.rows);
      }
      
      if (ws.configs_json) {
        const configs = JSON.parse(ws.configs_json);
        if (configs.plotType) setPlotType(configs.plotType);
        if (configs.xCol) setXCol(configs.xCol);
        if (configs.yCol) setYCol(configs.yCol);
        if (configs.colorCol) setColorCol(configs.colorCol);
        if (configs.selectedFeatures) setSelectedFeatures(configs.selectedFeatures);
        if (configs.perplexity) setPerplexity(configs.perplexity);
        if (configs.clusterAlgorithm) setClusterAlgorithm(configs.clusterAlgorithm);
        if (configs.nClusters) setNClusters(configs.nClusters);
        if (configs.eps) setEps(configs.eps);
        if (configs.doseConcCol) setDoseConcCol(configs.doseConcCol);
        if (configs.doseRespCol) setDoseRespCol(configs.doseRespCol);
        if (configs.doseGroupCol) setDoseGroupCol(configs.doseGroupCol);
      }

      setSelectedHistoryId(ws.query_history_id ? String(ws.query_history_id) : '');
      alert(`Loaded workspace: ${ws.name}`);
    } catch (e: any) {
      alert(`Failed to load workspace parameters: ${e.message}`);
    }
  };

  // Delete Workspace
  const handleDeleteWorkspace = async (e: any, id: number) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this workspace?")) return;
    try {
      await apiRequest(`/analytics/workspaces/${id}`, {
        service: 'query',
        method: 'DELETE'
      });
      loadMetadata();
    } catch (e: any) {
      alert(`Delete failed: ${e.message}`);
    }
  };

  // Plotly chart data formulations
  const scatterPlotData = useMemo(() => {
    if (rows.length === 0 || !xCol || !yCol) return [];
    const xIdx = columns.indexOf(xCol);
    const yIdx = columns.indexOf(yCol);
    const cIdx = colorCol ? columns.indexOf(colorCol) : -1;

    // If colored by cluster labels
    if (colorCol === '_cluster_labels_' && clusterLabels.length === rows.length) {
      const uniqueClusters = Array.from(new Set(clusterLabels));
      return uniqueClusters.map(label => {
        const cRows = rows.filter((_, idx) => clusterLabels[idx] === label);
        return {
          x: cRows.map(r => r[xIdx]),
          y: cRows.map(r => r[yIdx]),
          mode: 'markers',
          type: 'scatter',
          name: `Cluster ${label}`,
          marker: { size: 10 }
        };
      });
    }

    // Standard coloring by a categorical column
    if (cIdx !== -1) {
      const uniqueCategories = Array.from(new Set(rows.map(r => r[cIdx])));
      return uniqueCategories.map(cat => {
        const catRows = rows.filter(r => r[cIdx] === cat);
        return {
          x: catRows.map(r => r[xIdx]),
          y: catRows.map(r => r[yIdx]),
          mode: 'markers',
          type: 'scatter',
          name: String(cat),
          marker: { size: 9 }
        };
      });
    }

    return [{
      x: rows.map(r => r[xIdx]),
      y: rows.map(r => r[yIdx]),
      mode: 'markers',
      type: 'scatter',
      name: 'Datapoints',
      marker: { color: '#0ea5e9', size: 9 }
    }];
  }, [rows, columns, xCol, yCol, colorCol, clusterLabels]);

  // AG Grid columns configuration
  const gridColumnDefs = useMemo<ColDef[]>(() => {
    return columns.map(c => ({
      field: c,
      headerName: c.replace('_', ' ').toUpperCase(),
      sortable: true,
      filter: true,
      resizable: true
    }));
  }, [columns]);

  return (
    <div className="space-y-6 h-full flex flex-col pb-10">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-[#0c1220] border border-[#1e293b] p-5 rounded-2xl gap-4 flex-shrink-0">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2.5">
            <BarChart4 className="h-6 w-6 text-sky-400" />
            <span>Scientific Analytics Workbench</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Build exploratory plots, perform dimensions PCA/t-SNE maps, assign clusters, and calculate EC50 curves.
          </p>
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={loadDemoDataset}
            className="flex items-center space-x-1.5 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 hover:from-emerald-500/30 hover:to-teal-500/30 border border-emerald-500/30 text-emerald-400 text-xs font-bold px-4 py-2.5 rounded-xl transition-all cursor-pointer shadow-md"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>Load Demo Dataset</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-0">
        {/* Left Control Panel */}
        <div className="lg:col-span-1 space-y-5 overflow-y-auto pr-1 flex flex-col">
          {/* Query Selection & Loading */}
          <div className="glass-panel border border-slate-800 rounded-2xl p-5 space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
              <Database className="h-4 w-4 text-sky-400" />
              <span>Select Query Source</span>
            </h3>

            <div className="space-y-2">
              <select
                value={selectedHistoryId}
                onChange={(e) => handleQuerySelect(e.target.value)}
                className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-350 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500 cursor-pointer"
              >
                <option value="">-- Select execution history --</option>
                {queryHistory.map(h => (
                  <option key={h.id} value={String(h.id)}>
                    Query #{h.id} ({h.row_count} rows)
                  </option>
                ))}
              </select>
            </div>
            
            {loadingHistory && (
              <div className="flex items-center space-x-2 text-[10px] text-slate-400">
                <RefreshCw className="h-3 w-3 animate-spin text-sky-400" />
                <span>Syncing data stream...</span>
              </div>
            )}
            
            {rows.length > 0 && (
              <div className="flex justify-between text-[10px] text-slate-500 bg-slate-900/30 p-2.5 rounded-xl border border-slate-800/50">
                <span>Columns: <strong>{columns.length}</strong></span>
                <span>Rows Loaded: <strong>{rows.length}</strong></span>
              </div>
            )}
          </div>

          {/* Workspace persistence */}
          <div className="glass-panel border border-slate-800 rounded-2xl p-5 space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
              <Save className="h-4 w-4 text-sky-400" />
              <span>Save Workspace</span>
            </h3>

            <div className="space-y-2.5">
              <input
                type="text"
                value={currentWorkspaceName}
                onChange={(e) => setCurrentWorkspaceName(e.target.value)}
                placeholder="Workspace Name..."
                className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500"
              />
              <textarea
                value={currentWorkspaceDesc}
                onChange={(e) => setCurrentWorkspaceDesc(e.target.value)}
                placeholder="Description (optional)..."
                rows={2}
                className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-sky-500"
              />
              <button
                onClick={handleSaveWorkspace}
                disabled={rows.length === 0}
                className="w-full bg-sky-500 hover:bg-sky-600 disabled:opacity-40 text-white font-bold py-2 rounded-xl text-xs flex justify-center items-center space-x-1.5 shadow-md transition-all cursor-pointer"
              >
                <Save className="h-3.5 w-3.5" />
                <span>Save Current Workspace</span>
              </button>
            </div>
          </div>

          {/* Saved Workspaces */}
          {savedWorkspaces.length > 0 && (
            <div className="glass-panel border border-slate-800 rounded-2xl p-5 space-y-3 flex-1 overflow-y-auto max-h-[300px]">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2 border-b border-slate-850 pb-2 flex-shrink-0">
                <FolderOpen className="h-4 w-4 text-sky-400" />
                <span>Load Workspaces</span>
              </h3>
              
              <div className="space-y-2">
                {savedWorkspaces.map(ws => (
                  <div
                    key={ws.id}
                    onClick={() => handleLoadWorkspace(ws)}
                    className="p-2.5 bg-[#070b13] border border-slate-900 hover:border-slate-800 hover:bg-[#0d1322] rounded-xl cursor-pointer transition-all flex justify-between items-center group"
                  >
                    <div className="overflow-hidden pr-2">
                      <h4 className="text-[11px] font-bold text-white truncate">{ws.name}</h4>
                      <p className="text-[9px] text-slate-500 truncate">{ws.description || 'No description'}</p>
                    </div>
                    <button
                      onClick={(e) => handleDeleteWorkspace(e, ws.id)}
                      className="text-rose-500 hover:text-rose-400 p-1 hover:bg-rose-500/10 rounded-md transition-all flex-shrink-0 opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Main Work Area (Span 3) */}
        <div className="lg:col-span-3 flex flex-col space-y-5 h-full min-h-0 bg-[#070b13]/20 border border-[#1e293b]/60 rounded-2xl p-5">
          {/* Tab Navigation */}
          <div className="flex border-b border-slate-850 gap-2 flex-shrink-0">
            {[
              { id: 'grid', label: 'Data Grid' },
              { id: 'visuals', label: 'Exploratory Plots' },
              { id: 'dimred', label: 'PCA / t-SNE Map' },
              { id: 'clustering', label: 'Clustering' },
              { id: 'correlation', label: 'Correlation Heatmap' },
              { id: 'doseresp', label: 'Dose-Response (IC50)' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                disabled={rows.length === 0 && tab.id !== 'grid'}
                className={`px-4 py-2 border-b-2 font-semibold text-xs transition-all disabled:opacity-30 cursor-pointer ${
                  activeTab === tab.id
                    ? 'border-sky-500 text-sky-400'
                    : 'border-transparent text-slate-500 hover:text-slate-350'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex-1 min-h-0 relative">
            {rows.length === 0 ? (
              <div className="h-full flex flex-col justify-center items-center text-slate-500 space-y-4">
                <HelpCircle className="h-12 w-12 text-slate-700" />
                <div className="text-center space-y-1">
                  <h3 className="text-sm font-bold text-slate-400">Load a Dataset to Begin</h3>
                  <p className="text-xs text-slate-600 max-w-sm">
                    Select a query from the historical records on the left panel or click "Load Demo Dataset" for an instant chemistry demonstration.
                  </p>
                </div>
              </div>
            ) : (
              <div className="h-full overflow-y-auto">
                {/* 1. DATA GRID TAB */}
                {activeTab === 'grid' && (
                  <div className="h-full ag-theme-quartz-dark text-slate-100">
                    <AgGridReact
                      rowData={rows.map(r => {
                        const obj: any = {};
                        columns.forEach((col, idx) => {
                          obj[col] = r[idx];
                        });
                        return obj;
                      })}
                      columnDefs={gridColumnDefs}
                      pagination={true}
                      paginationPageSize={15}
                      defaultColDef={{
                        sortable: true,
                        filter: true,
                        resizable: true
                      }}
                    />
                  </div>
                )}

                {/* 2. EXPLORATORY VISUALS TAB */}
                {activeTab === 'visuals' && (
                  <div className="space-y-6 h-full overflow-y-auto pr-2 pb-8">
                    {/* KPI Cards Row */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="glass-panel border border-slate-800 rounded-xl p-4 flex items-center justify-between bg-[#070b13]/40">
                        <div>
                          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Filtered Records</p>
                          <h3 className="text-xl font-bold text-white mt-1">
                            {filteredRows.length} <span className="text-xs text-slate-400 font-normal">/ {rows.length}</span>
                          </h3>
                          <p className="text-[10px] text-sky-400 mt-0.5">
                            {rows.length > 0 ? ((filteredRows.length / rows.length) * 100).toFixed(0) : 0}% of total dataset
                          </p>
                        </div>
                        <Database className="h-8 w-8 text-sky-500/40" />
                      </div>

                      <div className="glass-panel border border-slate-800 rounded-xl p-4 flex items-center justify-between bg-[#070b13]/40">
                        <div>
                          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Dataset Schema</p>
                          <h3 className="text-xl font-bold text-white mt-1">
                            {columns.length} <span className="text-xs text-slate-400 font-normal">Columns</span>
                          </h3>
                          <p className="text-[10px] text-emerald-400 mt-0.5">
                            {columnProfiles.filter(p => p.type === 'numeric').length} Numeric | {columnProfiles.filter(p => p.type === 'categorical').length} Categorical
                          </p>
                        </div>
                        <Sliders className="h-8 w-8 text-emerald-500/40" />
                      </div>

                      <div className="glass-panel border border-slate-800 rounded-xl p-4 flex items-center justify-between bg-[#070b13]/40">
                        <div>
                          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                            {yCol ? `Average ${yCol}` : 'Average Metric'}
                          </p>
                          <h3 className="text-xl font-bold text-sky-400 mt-1">
                            {summaryStats ? summaryStats.avg.toFixed(2) : 'N/A'}
                          </h3>
                          <p className="text-[10px] text-slate-500 mt-0.5">
                            {summaryStats ? `Sum: ${summaryStats.sum.toLocaleString(undefined, {maximumFractionDigits: 1})}` : 'No numeric variable selected'}
                          </p>
                        </div>
                        <Activity className="h-8 w-8 text-sky-500/40" />
                      </div>

                      <div className="glass-panel border border-slate-800 rounded-xl p-4 flex items-center justify-between bg-[#070b13]/40">
                        <div>
                          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                            {yCol ? `Max ${yCol}` : 'Max Metric'}
                          </p>
                          <h3 className="text-xl font-bold text-purple-400 mt-1">
                            {summaryStats ? summaryStats.max.toFixed(2) : 'N/A'}
                          </h3>
                          <p className="text-[10px] text-slate-500 mt-0.5">
                            {summaryStats ? `StdDev: ±${summaryStats.stdDev.toFixed(2)}` : 'No numeric variable selected'}
                          </p>
                        </div>
                        <Sparkles className="h-8 w-8 text-purple-500/40" />
                      </div>
                    </div>

                    {/* Main Workbench Grid */}
                    <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 min-h-[600px]">
                      {/* Sidebar Controls */}
                      <div className="xl:col-span-1 flex flex-col space-y-4">
                        {/* 1. Configurator */}
                        <div className="glass-panel border border-slate-800 rounded-2xl p-4 space-y-4">
                          <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                            <div className="flex items-center space-x-1.5">
                              <Settings className="h-4 w-4 text-sky-400" />
                              <span className="text-[11px] font-bold text-white uppercase tracking-wider">Plot Configurator</span>
                            </div>
                            <span className="text-[10px] font-semibold text-slate-500 uppercase">Interactive</span>
                          </div>

                          <div className="space-y-3">
                            <div className="space-y-1">
                              <label className="text-[9px] font-bold uppercase text-slate-500 tracking-wider">Plot Type</label>
                              <select
                                value={plotType}
                                onChange={(e) => {
                                  setPlotType(e.target.value);
                                  if (['histogram', 'correlation_heatmap'].includes(e.target.value)) {
                                    setYCol('');
                                  }
                                }}
                                className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-300 px-3 py-1.5 rounded-lg focus:outline-none focus:border-sky-500 transition"
                              >
                                <option value="bar">Bar Chart</option>
                                <option value="horizontal_bar">Horizontal Bar Chart</option>
                                <option value="stacked_bar">Stacked Bar Chart</option>
                                <option value="line">Line Chart</option>
                                <option value="area">Area Chart</option>
                                <option value="pie">Pie Chart</option>
                                <option value="donut">Donut Chart</option>
                                <option value="scatter">Scatter Plot</option>
                                <option value="bubble">Bubble Chart</option>
                                <option value="histogram">Histogram</option>
                                <option value="box">Box Plot</option>
                                <option value="violin">Violin Plot</option>
                                <option value="heatmap">Heatmap (2D Density)</option>
                                <option value="correlation_heatmap">Correlation Heatmap</option>
                                <option value="treemap">Treemap</option>
                                <option value="waterfall">Waterfall Chart</option>
                                <option value="kpi_cards">KPI Card Visual</option>
                                <option value="timeseries">Time Series Chart</option>
                                <option value="distribution">Distribution Plot (Hist + Line)</option>
                              </select>
                            </div>

                            <div className="space-y-1">
                              <label className="text-[9px] font-bold uppercase text-slate-500 tracking-wider">X Axis (Categories / Trends)</label>
                              <select
                                value={xCol}
                                onChange={(e) => setXCol(e.target.value)}
                                className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-300 px-3 py-1.5 rounded-lg focus:outline-none focus:border-sky-500 transition"
                              >
                                <option value="">-- Select --</option>
                                {columns.map(c => <option key={c} value={c}>{c}</option>)}
                              </select>
                            </div>

                            {!['histogram', 'correlation_heatmap', 'distribution'].includes(plotType) && (
                              <div className="space-y-1">
                                <label className="text-[9px] font-bold uppercase text-slate-500 tracking-wider">Y Axis (Values)</label>
                                <select
                                  value={yCol}
                                  onChange={(e) => setYCol(e.target.value)}
                                  className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-300 px-3 py-1.5 rounded-lg focus:outline-none focus:border-sky-500 transition"
                                >
                                  <option value="">-- Select --</option>
                                  {columns.map(c => <option key={c} value={c}>{c}</option>)}
                                </select>
                              </div>
                            )}

                            {/* Aggregations */}
                            {!['scatter', 'bubble', 'histogram', 'box', 'violin', 'heatmap', 'correlation_heatmap', 'distribution'].includes(plotType) && (
                              <div className="space-y-1">
                                <label className="text-[9px] font-bold uppercase text-slate-500 tracking-wider">Aggregation (Y values)</label>
                                <select
                                  value={aggregation}
                                  onChange={(e) => setAggregation(e.target.value)}
                                  className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-300 px-3 py-1.5 rounded-lg focus:outline-none focus:border-sky-500 transition"
                                >
                                  <option value="None">None (Sum by default)</option>
                                  <option value="Sum">Sum</option>
                                  <option value="Avg">Average</option>
                                  <option value="Min">Minimum</option>
                                  <option value="Max">Maximum</option>
                                  <option value="Count">Count</option>
                                </select>
                              </div>
                            )}

                            {/* Grouping */}
                            {['bar', 'stacked_bar', 'line', 'area', 'scatter', 'timeseries'].includes(plotType) && (
                              <div className="space-y-1">
                                <label className="text-[9px] font-bold uppercase text-slate-500 tracking-wider">Split / Color By</label>
                                <select
                                  value={plotType === 'scatter' ? colorCol : groupByCol}
                                  onChange={(e) => {
                                    if (plotType === 'scatter') {
                                      setColorCol(e.target.value);
                                    } else {
                                      setGroupByCol(e.target.value);
                                    }
                                  }}
                                  className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-300 px-3 py-1.5 rounded-lg focus:outline-none focus:border-sky-500 transition"
                                >
                                  <option value="">-- None --</option>
                                  {columns.map(c => <option key={c} value={c}>{c}</option>)}
                                </select>
                              </div>
                            )}

                            {/* Sorting */}
                            {!['scatter', 'bubble', 'histogram', 'box', 'violin', 'heatmap', 'correlation_heatmap', 'distribution'].includes(plotType) && (
                              <div className="grid grid-cols-2 gap-2 pt-1">
                                <div className="space-y-1">
                                  <label className="text-[9px] font-bold uppercase text-slate-500 tracking-wider">Sort By</label>
                                  <select
                                    value={sortBy}
                                    onChange={(e) => setSortBy(e.target.value)}
                                    className="w-full bg-[#070b13] border border-slate-800 text-[10px] text-slate-300 px-2 py-1 rounded focus:outline-none focus:border-sky-500 transition"
                                  >
                                    <option value="none">Default</option>
                                    <option value="x">X Axis</option>
                                    <option value="y">Y Axis</option>
                                  </select>
                                </div>
                                <div className="space-y-1">
                                  <label className="text-[9px] font-bold uppercase text-slate-500 tracking-wider">Order</label>
                                  <select
                                    value={sortOrder}
                                    onChange={(e) => setSortOrder(e.target.value)}
                                    className="w-full bg-[#070b13] border border-slate-800 text-[10px] text-slate-300 px-2 py-1 rounded focus:outline-none focus:border-sky-500 transition"
                                  >
                                    <option value="asc">Ascending</option>
                                    <option value="desc">Descending</option>
                                  </select>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* 2. Interactive Global Filters */}
                        <div className="glass-panel border border-slate-800 rounded-2xl p-4 space-y-3">
                          <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                            <div className="flex items-center space-x-1.5">
                              <Filter className="h-4 w-4 text-emerald-400" />
                              <span className="text-[11px] font-bold text-white uppercase tracking-wider">Interactive Filters</span>
                            </div>
                            {Object.keys(activeFilters).length > 0 && (
                              <button
                                onClick={() => setActiveFilters({})}
                                className="text-[9px] text-red-400 hover:text-red-300 font-semibold uppercase"
                              >
                                Clear All
                              </button>
                            )}
                          </div>

                          <div className="space-y-3 max-h-[220px] overflow-y-auto pr-1">
                            {columnProfiles.filter(p => ['numeric', 'categorical'].includes(p.type)).map(profile => {
                              const isNumeric = profile.type === 'numeric';
                              return (
                                <div key={profile.name} className="space-y-1 border-b border-slate-850/50 pb-2 last:border-b-0 last:pb-0">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-semibold text-slate-300">{profile.name}</span>
                                    <span className="text-[9px] text-slate-500 capitalize">{profile.type}</span>
                                  </div>
                                  
                                  {isNumeric ? (
                                    <div className="space-y-1 pt-1">
                                      <div className="flex justify-between text-[9px] text-slate-400">
                                        <span>Min: {profile.min !== undefined ? profile.min.toFixed(1) : ''}</span>
                                        <span>Max: {profile.max !== undefined ? profile.max.toFixed(1) : ''}</span>
                                      </div>
                                      <div className="flex space-x-2">
                                        <input
                                          type="number"
                                          placeholder="Min"
                                          value={activeFilters[profile.name]?.min ?? ''}
                                          onChange={(e) => {
                                            const minVal = e.target.value !== '' ? Number(e.target.value) : undefined;
                                            setActiveFilters(prev => ({
                                              ...prev,
                                              [profile.name]: { ...prev[profile.name], min: minVal }
                                            }));
                                          }}
                                          className="w-1/2 bg-[#070b13] border border-slate-800 text-[10px] text-slate-300 px-2 py-1 rounded"
                                        />
                                        <input
                                          type="number"
                                          placeholder="Max"
                                          value={activeFilters[profile.name]?.max ?? ''}
                                          onChange={(e) => {
                                            const maxVal = e.target.value !== '' ? Number(e.target.value) : undefined;
                                            setActiveFilters(prev => ({
                                              ...prev,
                                              [profile.name]: { ...prev[profile.name], max: maxVal }
                                            }));
                                          }}
                                          className="w-1/2 bg-[#070b13] border border-slate-800 text-[10px] text-slate-300 px-2 py-1 rounded"
                                        />
                                      </div>
                                    </div>
                                  ) : (
                                    <div className="flex flex-wrap gap-1 pt-1">
                                      {profile.distinctValues.slice(0, 8).map(valStr => {
                                        const val = String(valStr);
                                        const isChecked = activeFilters[profile.name]?.includes(val) ?? false;
                                        return (
                                          <button
                                            key={val}
                                            onClick={() => {
                                              const currentList = activeFilters[profile.name] || [];
                                              const newList = isChecked
                                                ? currentList.filter((v: string) => v !== val)
                                                : [...currentList, val];
                                              setActiveFilters(prev => ({
                                                ...prev,
                                                [profile.name]: newList.length > 0 ? newList : undefined
                                              }));
                                            }}
                                            className={`text-[9px] px-2 py-0.5 rounded border transition font-medium ${
                                              isChecked
                                                ? 'bg-emerald-500/25 border-emerald-500/50 text-emerald-300'
                                                : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
                                            }`}
                                          >
                                            {val}
                                          </button>
                                        );
                                      })}
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>

                        {/* 3. AI/Intelligent Recommendations */}
                        <div className="glass-panel border border-slate-800 rounded-2xl p-4 space-y-3">
                          <div className="flex items-center space-x-1.5 border-b border-slate-850 pb-2">
                            <Sparkles className="h-4 w-4 text-purple-400" />
                            <span className="text-[11px] font-bold text-white uppercase tracking-wider">Smart Suggestions</span>
                          </div>

                          <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
                            {chartRecommendations.length === 0 ? (
                              <p className="text-[10px] text-slate-500 italic">No recommendations available for the current dataset structure.</p>
                            ) : (
                              chartRecommendations.map((rec, idx) => (
                                <button
                                  key={idx}
                                  onClick={() => {
                                    setPlotType(rec.chartType);
                                    setXCol(rec.xCol);
                                    setYCol(rec.yCol);
                                    if (rec.colorByCol) setColorCol(rec.colorByCol);
                                    if (rec.groupByCol) setGroupByCol(rec.groupByCol ?? '');
                                    if (rec.aggregation) setAggregation(rec.aggregation);
                                  }}
                                  className="w-full text-left bg-slate-950/40 hover:bg-slate-900/60 border border-slate-850 hover:border-purple-500/30 rounded-xl p-2.5 transition space-y-1 block"
                                >
                                  <div className="flex items-center justify-between">
                                    <span className="text-[10px] font-bold text-purple-300">{rec.title}</span>
                                    <span className="text-[8px] bg-purple-500/25 text-purple-300 px-1.5 py-0.5 rounded font-mono uppercase">
                                      {rec.chartType}
                                    </span>
                                  </div>
                                  <p className="text-[9px] text-slate-400 leading-normal">{rec.reason}</p>
                                </button>
                              ))
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Main Chart Canvas Area */}
                      <div className="xl:col-span-3 flex flex-col space-y-6">
                        {/* Chart Area Card */}
                        <div className={`glass-panel border border-slate-800 rounded-3xl p-6 relative flex flex-col ${
                          isFullscreen ? 'fixed inset-0 z-50 bg-[#02060f]/95 overflow-y-auto p-8' : 'min-h-[500px]'
                        }`}>
                          {/* Canvas Header */}
                          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-850 pb-4 mb-4">
                            <div className="space-y-1">
                              <div className="flex items-center space-x-2">
                                <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                                  {plotType.replace('_', ' ').toUpperCase()} VIEW
                                </h2>
                                {drillDownPath.length > 0 && (
                                  <span className="text-[9px] bg-amber-500/25 text-amber-300 px-2 py-0.5 rounded font-mono">
                                    Drill Down Active
                                  </span>
                                )}
                              </div>
                              <p className="text-[10px] text-slate-500">
                                {xCol ? `${xCol}` : 'No variable selected'} 
                                {yCol ? ` vs ${yCol}` : ''}
                                {aggregation !== 'None' ? ` (Aggregated: ${aggregation})` : ''}
                              </p>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex items-center space-x-2">
                              {drillDownPath.length > 0 && (
                                <button
                                  onClick={handleDrillUp}
                                  className="flex items-center space-x-1 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 px-2.5 py-1.5 rounded-lg border border-amber-500/25 text-[10px] font-semibold transition"
                                >
                                  <ArrowLeft className="h-3 w-3" />
                                  <span>Drill Up</span>
                                </button>
                              )}

                              <button
                                onClick={exportPNG}
                                disabled={!plotlyRef}
                                className="flex items-center space-x-1 bg-slate-900 hover:bg-slate-850 text-slate-300 disabled:opacity-50 px-2.5 py-1.5 rounded-lg border border-slate-800 text-[10px] font-semibold transition"
                                title="Export as PNG Image"
                              >
                                <Download className="h-3 w-3 text-sky-400" />
                                <span>PNG</span>
                              </button>

                              <button
                                onClick={exportSVG}
                                disabled={!plotlyRef}
                                className="flex items-center space-x-1 bg-slate-900 hover:bg-slate-850 text-slate-300 disabled:opacity-50 px-2.5 py-1.5 rounded-lg border border-slate-800 text-[10px] font-semibold transition"
                                title="Export as Vector SVG"
                              >
                                <Download className="h-3 w-3 text-purple-400" />
                                <span>SVG</span>
                              </button>

                              <button
                                onClick={() => setIsFullscreen(!isFullscreen)}
                                className="flex items-center space-x-1 bg-slate-900 hover:bg-slate-850 text-slate-300 px-2.5 py-1.5 rounded-lg border border-slate-800 text-[10px] font-semibold transition"
                              >
                                {isFullscreen ? (
                                  <>
                                    <Minimize2 className="h-3 w-3 text-emerald-400" />
                                    <span>Exit Fullscreen</span>
                                  </>
                                ) : (
                                  <>
                                    <Maximize2 className="h-3 w-3 text-emerald-400" />
                                    <span>Fullscreen</span>
                                  </>
                                )}
                              </button>
                            </div>
                          </div>

                          {/* Drilldown Filter Breadcrumbs */}
                          {drillDownPath.length > 0 && (
                            <div className="flex items-center space-x-1.5 bg-amber-500/5 border border-amber-500/10 rounded-lg p-2 mb-4 text-[10px] text-amber-300/90">
                              <Info className="h-3.5 w-3.5 text-amber-400 flex-shrink-0" />
                              <div className="flex items-center flex-wrap gap-1 font-mono">
                                <span className="font-sans font-semibold text-slate-400 mr-1">Drill path:</span>
                                {drillDownPath.map((path, idx) => (
                                  <span key={idx} className="flex items-center">
                                    <span className="bg-amber-500/15 px-2 py-0.5 rounded border border-amber-500/20">{path}</span>
                                    {idx < drillDownPath.length - 1 && <span className="mx-1 text-slate-600">&gt;</span>}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* The Plotly Component */}
                          <div className="flex-1 flex justify-center items-center bg-[#070b13]/30 border border-slate-850/50 rounded-2xl p-4 min-h-[350px]">
                            {(!xCol || (!['histogram', 'correlation_heatmap', 'distribution'].includes(plotType) && !yCol)) ? (
                              <div className="text-center space-y-2 max-w-sm">
                                <BarChart4 className="h-10 w-10 text-slate-700 mx-auto" />
                                <h4 className="text-xs font-bold text-slate-400">Plot Unconfigured</h4>
                                <p className="text-[10px] text-slate-600 leading-relaxed">
                                  Select an X-Axis variable and Y-Axis values inside the configurator panel, or click one of our Smart Suggestions to configure instantly.
                                </p>
                              </div>
                            ) : (
                              <Plot
                                data={plotlyData}
                                layout={{
                                  paper_bgcolor: 'rgba(0,0,0,0)',
                                  plot_bgcolor: 'rgba(0,0,0,0)',
                                  font: { color: '#94a3b8', size: 10 },
                                  xaxis: { 
                                    title: xCol, 
                                    gridcolor: '#1e293b', 
                                    zerolinecolor: '#334155',
                                    tickfont: { color: '#64748b' }
                                  },
                                  yaxis: { 
                                    title: yCol || 'Value / Count', 
                                    gridcolor: '#1e293b', 
                                    zerolinecolor: '#334155',
                                    tickfont: { color: '#64748b' }
                                  },
                                  autosize: true,
                                  margin: { l: 60, r: 30, t: 30, b: 60 },
                                  barmode: plotType === 'stacked_bar' ? 'stack' : 'group',
                                  showlegend: true,
                                  legend: { font: { color: '#94a3b8' } }
                                }}
                                config={{ responsive: true, displayModeBar: false }}
                                onInitialized={(figure, graphDiv) => setPlotlyRef(graphDiv)}
                                onUpdate={(figure, graphDiv) => setPlotlyRef(graphDiv)}
                                onClick={(data) => {
                                  if (!data || !data.points || data.points.length === 0) return;
                                  const pt = data.points[0];
                                  const clickVal = pt.x ?? pt.label;
                                  if (clickVal !== undefined) handleChartClick(clickVal);
                                }}
                                style={{ width: '100%', height: '100%', minHeight: '380px' }}
                              />
                            )}
                          </div>
                        </div>

                        {/* Multi-Chart Companion / Cross-Filter Section (Tableau / Power BI experience) */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                          {/* Companion Chart 1: Categorical breakdown cross-filter */}
                          <div className="glass-panel border border-slate-800 rounded-2xl p-4 space-y-3 md:col-span-2">
                            <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                              <span className="text-[10px] font-bold text-slate-300 uppercase tracking-wider">
                                Companion 1: Categorical Distribution
                              </span>
                              <span className="text-[8px] bg-sky-500/25 text-sky-400 px-1.5 py-0.5 rounded font-mono">
                                Click to Cross-Filter
                              </span>
                            </div>
                            
                            <div className="h-[200px] flex justify-center items-center">
                              {columnProfiles.filter(p => p.type === 'categorical').length === 0 ? (
                                <p className="text-[10px] text-slate-600">No categorical columns available for companion chart.</p>
                              ) : (
                                <Plot
                                  data={[{
                                    labels: Array.from(new Set(filteredRows.map(r => String(r[columns.indexOf(columnProfiles.filter(p => p.type === 'categorical')[0].name)])))),
                                    values: Array.from(new Set(filteredRows.map(r => String(r[columns.indexOf(columnProfiles.filter(p => p.type === 'categorical')[0].name)])))).map(cVal => 
                                      filteredRows.filter(r => String(r[columns.indexOf(columnProfiles.filter(p => p.type === 'categorical')[0].name)]) === cVal).length
                                    ),
                                    type: 'pie',
                                    hole: 0.4
                                  }]}
                                  layout={{
                                    paper_bgcolor: 'rgba(0,0,0,0)',
                                    plot_bgcolor: 'rgba(0,0,0,0)',
                                    font: { color: '#94a3b8', size: 8 },
                                    showlegend: true,
                                    legend: { font: { size: 8, color: '#94a3b8' } },
                                    margin: { l: 20, r: 20, t: 10, b: 20 }
                                  }}
                                  config={{ responsive: true, displayModeBar: false }}
                                  onClick={(data) => {
                                    if (!data || !data.points || data.points.length === 0) return;
                                    const cCol = columnProfiles.filter(p => p.type === 'categorical')[0].name;
                                    const clickVal = data.points[0].label;
                                    
                                    const currentFilter = activeFilters[cCol] || [];
                                    const isSelected = currentFilter.includes(clickVal);
                                    const newFilter = isSelected 
                                      ? currentFilter.filter((v: any) => v !== clickVal)
                                      : [...currentFilter, clickVal];
                                      
                                    setActiveFilters(prev => ({
                                      ...prev,
                                      [cCol]: newFilter.length > 0 ? newFilter : undefined
                                    }));
                                  }}
                                  style={{ width: '100%', height: '100%' }}
                                />
                              )}
                            </div>
                          </div>

                          {/* Summary Statistics Table card */}
                          <div className="glass-panel border border-slate-800 rounded-2xl p-4 space-y-3 md:col-span-1">
                            <div className="flex items-center space-x-1.5 border-b border-slate-850 pb-2">
                              <Table className="h-4 w-4 text-sky-400" />
                              <span className="text-[10px] font-bold text-white uppercase tracking-wider">Summary Stats</span>
                            </div>

                            {!summaryStats ? (
                              <div className="h-[180px] flex items-center justify-center text-center p-4">
                                <p className="text-[10px] text-slate-600 leading-normal">
                                  Select a numeric Y-Axis variable to compute scientific statistics.
                                </p>
                              </div>
                            ) : (
                              <div className="space-y-1.5 text-[10px]">
                                <div className="flex justify-between border-b border-slate-850 py-1">
                                  <span className="text-slate-500">Record Count</span>
                                  <span className="text-slate-300 font-mono font-semibold">{summaryStats.count}</span>
                                </div>
                                <div className="flex justify-between border-b border-slate-850 py-1">
                                  <span className="text-slate-500">Average</span>
                                  <span className="text-slate-300 font-mono font-semibold">{summaryStats.avg.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between border-b border-slate-850 py-1">
                                  <span className="text-slate-500">Median</span>
                                  <span className="text-slate-300 font-mono font-semibold">{summaryStats.median.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between border-b border-slate-850 py-1">
                                  <span className="text-slate-500">Std Deviation</span>
                                  <span className="text-slate-300 font-mono font-semibold">±{summaryStats.stdDev.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between border-b border-slate-850 py-1">
                                  <span className="text-slate-500">Minimum</span>
                                  <span className="text-slate-300 font-mono font-semibold">{summaryStats.min.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between py-1">
                                  <span className="text-slate-500">Maximum</span>
                                  <span className="text-slate-300 font-mono font-semibold">{summaryStats.max.toFixed(2)}</span>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 3. DIMENSION REDUCTION TAB */}
                {activeTab === 'dimred' && (
                  <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full min-h-0">
                    <div className="lg:col-span-1 glass-panel border border-slate-800 rounded-2xl p-4 space-y-4">
                      <div className="flex items-center space-x-1.5 border-b border-slate-850 pb-2">
                        <Settings className="h-4 w-4 text-sky-400" />
                        <span className="text-[11px] font-bold text-white uppercase tracking-wider">Features Selection</span>
                      </div>
                      
                      <div className="space-y-3">
                        <p className="text-[10px] text-slate-500 leading-relaxed">
                          Select the numeric parameters to scale and project:
                        </p>
                        
                        <div className="max-h-[150px] overflow-y-auto border border-slate-850 rounded-lg p-2.5 space-y-1.5 bg-[#070b13]/50">
                          {numericCols.map(col => (
                            <label key={col} className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer">
                              <input
                                type="checkbox"
                                checked={selectedFeatures.includes(col)}
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    setSelectedFeatures([...selectedFeatures, col]);
                                  } else {
                                    setSelectedFeatures(selectedFeatures.filter(f => f !== col));
                                  }
                                }}
                                className="rounded bg-slate-900 border-slate-800 text-sky-500 accent-sky-500"
                              />
                              <span>{col}</span>
                            </label>
                          ))}
                        </div>

                        <div className="pt-2.5 border-t border-slate-850/60 space-y-2">
                          <button
                            onClick={executePCA}
                            disabled={pcaLoading || selectedFeatures.length < 2}
                            className="w-full bg-sky-500 hover:bg-sky-600 disabled:opacity-40 text-white font-bold py-1.5 rounded-lg text-xs transition-colors flex justify-center items-center space-x-1"
                          >
                            <span>{pcaLoading ? 'Projecting PCA...' : 'Compute PCA'}</span>
                          </button>

                          <div className="space-y-1.5 pt-2">
                            <label className="text-[9px] font-bold uppercase text-slate-500 tracking-wider block">t-SNE Perplexity</label>
                            <input
                              type="number"
                              min="2"
                              max="50"
                              value={perplexity}
                              onChange={(e) => setPerplexity(Number(e.target.value))}
                              className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-1 rounded-lg focus:outline-none"
                            />
                            <button
                              onClick={executeTSNE}
                              disabled={tsneLoading || selectedFeatures.length < 2 || rows.length < 5}
                              className="w-full bg-teal-500 hover:bg-teal-600 disabled:opacity-40 text-white font-bold py-1.5 rounded-lg text-xs transition-colors flex justify-center items-center space-x-1"
                            >
                              <span>{tsneLoading ? 'Computing t-SNE...' : 'Compute t-SNE'}</span>
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="lg:col-span-3 space-y-4">
                      {/* PCA Plot */}
                      {pcaCoords.length > 0 && (
                        <div className="bg-[#070b13]/30 border border-slate-850 rounded-2xl p-4 min-h-[300px]">
                          <Plot
                            data={[{
                              x: pcaCoords.map(c => c.pc1),
                              y: pcaCoords.map(c => c.pc2),
                              mode: 'markers',
                              type: 'scatter',
                              name: 'PCA Projections',
                              marker: { color: '#0ea5e9', size: 9 }
                            }]}
                            layout={{
                              paper_bgcolor: 'rgba(0,0,0,0)',
                              plot_bgcolor: 'rgba(0,0,0,0)',
                              title: { text: `PCA Map (PC1: ${(explainedVar[0]*100).toFixed(1)}%, PC2: ${(explainedVar[1]*100).toFixed(1)}%)`, font: { color: '#fff', size: 12 } },
                              font: { color: '#94a3b8', size: 10 },
                              xaxis: { title: 'Principal Component 1', gridcolor: '#1e293b' },
                              yaxis: { title: 'Principal Component 2', gridcolor: '#1e293b' },
                              autosize: true
                            }}
                            config={{ responsive: true }}
                            style={{ width: '100%', height: '100%', minHeight: '280px' }}
                          />

                          {pcaLoadings.length > 0 && (
                            <div className="mt-4 bg-[#0c1220] border border-slate-800 rounded-xl p-4 space-y-2">
                              <h4 className="text-[10px] font-bold uppercase text-slate-500 tracking-wider">PCA Component Loadings (Coefficients)</h4>
                              <div className="overflow-x-auto">
                                <table className="w-full text-[11px] text-left text-slate-300">
                                  <thead>
                                    <tr className="border-b border-slate-800 text-[10px] text-slate-400 font-bold uppercase">
                                      <th className="py-2">Feature</th>
                                      <th className="py-2 text-right">PC 1 loading</th>
                                      <th className="py-2 text-right">PC 2 loading</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {pcaLoadings.map((load: any, idx: number) => (
                                      <tr key={idx} className="border-b border-slate-900">
                                        <td className="py-2 font-semibold text-white">{load.feature}</td>
                                        <td className="py-2 text-right font-mono text-sky-400">{load.pc1.toFixed(4)}</td>
                                        <td className="py-2 text-right font-mono text-emerald-400">{load.pc2.toFixed(4)}</td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          )}

                          {pcaLoadingError && (
                            <div className="mt-4 bg-rose-500/10 border border-rose-500/20 text-rose-450 p-3 rounded-xl text-xs">
                              Error: {pcaLoadingError}
                            </div>
                          )}
                        </div>
                      )}

                      {/* t-SNE Plot */}
                      {tsneCoords.length > 0 && (
                        <div className="bg-[#070b13]/30 border border-slate-850 rounded-2xl p-4 min-h-[300px]">
                          <Plot
                            data={[{
                              x: tsneCoords.map(c => c.x),
                              y: tsneCoords.map(c => c.y),
                              mode: 'markers',
                              type: 'scatter',
                              name: 't-SNE Map',
                              marker: { color: '#10b981', size: 9 }
                            }]}
                            layout={{
                              paper_bgcolor: 'rgba(0,0,0,0)',
                              plot_bgcolor: 'rgba(0,0,0,0)',
                              title: { text: `t-SNE Map (Perplexity: ${perplexity})`, font: { color: '#fff', size: 12 } },
                              font: { color: '#94a3b8', size: 10 },
                              xaxis: { title: 't-SNE Dimension 1', gridcolor: '#1e293b' },
                              yaxis: { title: 't-SNE Dimension 2', gridcolor: '#1e293b' },
                              autosize: true
                            }}
                            config={{ responsive: true }}
                            style={{ width: '100%', height: '100%', minHeight: '280px' }}
                          />
                        </div>
                      )}

                      {pcaCoords.length === 0 && tsneCoords.length === 0 && (
                        <div className="h-full flex justify-center items-center p-10 text-slate-600 font-semibold border border-dashed border-slate-800 rounded-2xl min-h-[300px]">
                          Select feature columns and compute PCA / t-SNE map to visualize.
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* 4. CLUSTERING TAB */}
                {activeTab === 'clustering' && (
                  <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full min-h-0">
                    <div className="lg:col-span-1 glass-panel border border-slate-800 rounded-2xl p-4 space-y-4">
                      <div className="flex items-center space-x-1.5 border-b border-slate-850 pb-2">
                        <Settings className="h-4 w-4 text-sky-400" />
                        <span className="text-[11px] font-bold text-white uppercase tracking-wider">Clustering Config</span>
                      </div>
                      
                      <div className="space-y-3">
                        <div className="space-y-1">
                          <label className="text-[9px] font-bold uppercase text-slate-500 tracking-wider">Algorithm</label>
                          <select
                            value={clusterAlgorithm}
                            onChange={(e) => setClusterAlgorithm(e.target.value as any)}
                            className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-350 px-3 py-1.5 rounded-lg focus:outline-none"
                          >
                            <option value="kmeans">K-Means Clustering</option>
                            <option value="dbscan">DBSCAN (Density-Based)</option>
                          </select>
                        </div>

                        {clusterAlgorithm === 'kmeans' ? (
                          <div className="space-y-1">
                            <label className="text-[9px] font-bold uppercase text-slate-500 tracking-wider block">Number of Clusters (K)</label>
                            <input
                              type="number"
                              min="2"
                              max="10"
                              value={nClusters}
                              onChange={(e) => setNClusters(Number(e.target.value))}
                              className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-1 rounded-lg focus:outline-none"
                            />
                          </div>
                        ) : (
                          <div className="space-y-1">
                            <label className="text-[9px] font-bold uppercase text-slate-500 tracking-wider block">Eps (Radius)</label>
                            <input
                              type="number"
                              step="0.05"
                              value={eps}
                              onChange={(e) => setEps(Number(e.target.value))}
                              className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-200 px-3 py-1 rounded-lg focus:outline-none"
                            />
                          </div>
                        )}

                        <button
                          onClick={executeClustering}
                          disabled={clusterLoading || selectedFeatures.length < 2}
                          className="w-full bg-sky-500 hover:bg-sky-600 disabled:opacity-40 text-white font-bold py-1.5 rounded-lg text-xs transition-colors flex justify-center items-center space-x-1"
                        >
                          <span>{clusterLoading ? 'Running...' : 'Run Clustering'}</span>
                        </button>
                      </div>
                    </div>

                    <div className="lg:col-span-3">
                      {clusterLabels.length > 0 ? (
                        <div className="bg-[#0c1220] border border-slate-800 rounded-2xl p-5 space-y-4">
                          <div className="flex items-center space-x-2 text-emerald-400 text-xs font-bold uppercase">
                            <CheckCircle2 className="h-4 w-4" />
                            <span>Clusters Assigned Successfully</span>
                          </div>
                          
                          <p className="text-xs text-slate-400 leading-relaxed">
                            Cluster labels have been successfully appended as a coloring variable. Go to the <strong>Exploratory Plots</strong> tab and choose <strong>Clustering Labels</strong> as the color grouping to view.
                          </p>
                          
                          <div className="border border-slate-850 bg-[#070b13]/50 p-4 rounded-xl space-y-2 max-h-[200px] overflow-y-auto">
                            <h4 className="text-[10px] font-bold uppercase text-slate-500 tracking-wider">Cluster Allocation details:</h4>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                              {Array.from(new Set(clusterLabels)).map(label => (
                                <div key={label} className="bg-slate-900 border border-slate-800 p-2.5 rounded-lg">
                                  <span className="text-[10px] text-slate-500 font-semibold block">Cluster {label}</span>
                                  <span className="text-sm font-extrabold text-white">
                                    {clusterLabels.filter(l => l === label).length} points
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="h-full flex justify-center items-center p-10 text-slate-600 font-semibold border border-dashed border-slate-800 rounded-2xl min-h-[300px]">
                          Select feature columns and click "Run Clustering" to assign partition variables.
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* 5. CORRELATION TAB */}
                {activeTab === 'correlation' && (
                  <div className="space-y-4 min-h-[400px]">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-slate-400 font-bold">Pearson correlation matrix of numerical features.</span>
                      <button
                        onClick={executeCorrelation}
                        disabled={corrLoading}
                        className="bg-sky-500 hover:bg-sky-600 disabled:opacity-50 text-white font-bold px-4 py-1.5 rounded-lg text-xs transition-colors flex justify-center items-center space-x-1.5 cursor-pointer"
                      >
                        {corrLoading && <RefreshCw className="h-3.5 w-3.5 animate-spin" />}
                        <span>{corrLoading ? 'Calculating...' : 'Compute Matrix'}</span>
                      </button>
                    </div>

                    {corrMatrix.length > 0 ? (
                      <div className="bg-[#070b13]/30 border border-slate-855 rounded-2xl p-4 flex justify-center items-center">
                        <Plot
                          data={[{
                            z: corrMatrix,
                            x: corrColumns,
                            y: corrColumns,
                            type: 'heatmap',
                            colorscale: 'RdBu',
                            zmin: -1,
                            zmax: 1
                          }]}
                          layout={{
                            paper_bgcolor: 'rgba(0,0,0,0)',
                            plot_bgcolor: 'rgba(0,0,0,0)',
                            title: { text: 'Pearson Correlation Coefficients', font: { color: '#fff', size: 12 } },
                            font: { color: '#94a3b8', size: 10 },
                            autosize: true,
                            margin: { l: 80, r: 20, t: 40, b: 80 }
                          }}
                          config={{ responsive: true }}
                          style={{ width: '100%', height: '100%', minHeight: '380px' }}
                        />
                      </div>
                    ) : (
                      <div className="flex justify-center items-center p-10 text-slate-600 font-semibold border border-dashed border-slate-800 rounded-2xl min-h-[300px]">
                        Click "Compute Matrix" to evaluate collinearity between numeric columns.
                      </div>
                    )}
                  </div>
                )}

                {/* 6. DOSE RESPONSE (IC50) TAB */}
                {activeTab === 'doseresp' && (
                  <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full min-h-0">
                    <div className="lg:col-span-1 glass-panel border border-slate-800 rounded-2xl p-4 space-y-4">
                      <div className="flex items-center space-x-1.5 border-b border-slate-850 pb-2">
                        <Activity className="h-4 w-4 text-sky-400" />
                        <span className="text-[11px] font-bold text-white uppercase tracking-wider">IC50 Curve Fitting</span>
                      </div>
                      
                      <div className="space-y-3">
                        <div className="space-y-1">
                          <label className="text-[9px] font-bold uppercase text-slate-500 tracking-wider">Concentration (X)</label>
                          <select
                            value={doseConcCol}
                            onChange={(e) => setDoseConcCol(e.target.value)}
                            className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-350 px-3 py-1.5 rounded-lg focus:outline-none"
                          >
                            <option value="">-- Select --</option>
                            {numericCols.map(c => <option key={c} value={c}>{c}</option>)}
                          </select>
                        </div>

                        <div className="space-y-1">
                          <label className="text-[9px] font-bold uppercase text-slate-500 tracking-wider">Response % (Y)</label>
                          <select
                            value={doseRespCol}
                            onChange={(e) => setDoseRespCol(e.target.value)}
                            className="w-full bg-[#070b13] border border-slate-800 text-xs text-slate-350 px-3 py-1.5 rounded-lg focus:outline-none"
                          >
                            <option value="">-- Select --</option>
                            {numericCols.map(c => <option key={c} value={c}>{c}</option>)}
                          </select>
                        </div>

                        <button
                          onClick={executeDoseResponseFit}
                          disabled={doseFitting || !doseConcCol || !doseRespCol}
                          className="w-full bg-emerald-500 hover:bg-emerald-600 disabled:opacity-40 text-white font-bold py-1.5 rounded-lg text-xs transition-colors flex justify-center items-center space-x-1 cursor-pointer"
                        >
                          <span>{doseFitting ? 'Fitting regression...' : 'Fit Sigmoidal Curve'}</span>
                        </button>
                      </div>
                    </div>

                    <div className="lg:col-span-3 space-y-4">
                      {doseFitResults ? (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="md:col-span-2 bg-[#070b13]/30 border border-slate-850 rounded-2xl p-4 min-h-[300px]">
                            <Plot
                              data={[
                                {
                                  x: rows.map(r => Number(r[columns.indexOf(doseConcCol)])),
                                  y: rows.map(r => Number(r[columns.indexOf(doseRespCol)])),
                                  mode: 'markers',
                                  type: 'scatter',
                                  name: 'Raw Data',
                                  marker: { color: '#f43f5e', size: 8 }
                                },
                                {
                                  x: doseFitResults.curve_points.concentrations,
                                  y: doseFitResults.curve_points.responses,
                                  mode: 'lines',
                                  type: 'scatter',
                                  name: '4PL Fit',
                                  line: { color: '#10b981', width: 2.5 }
                                }
                              ]}
                              layout={{
                                paper_bgcolor: 'rgba(0,0,0,0)',
                                plot_bgcolor: 'rgba(0,0,0,0)',
                                title: { text: 'Dose Response Sigmoidal Curve (4PL Fit)', font: { color: '#fff', size: 12 } },
                                font: { color: '#94a3b8', size: 10 },
                                xaxis: { title: 'Concentration (Log Scale)', type: 'log', gridcolor: '#1e293b' },
                                yaxis: { title: 'Response (%)', gridcolor: '#1e293b' },
                                autosize: true
                              }}
                              config={{ responsive: true }}
                              style={{ width: '100%', height: '100%', minHeight: '280px' }}
                            />
                          </div>

                          <div className="md:col-span-1 bg-slate-900/40 border border-slate-850 p-4 rounded-2xl flex flex-col justify-between">
                            <div className="space-y-4">
                              <h4 className="text-xs font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-2">Fit Outputs</h4>
                              
                              <div className="space-y-2">
                                <div className="p-2.5 bg-slate-950/40 rounded-xl">
                                  <span className="text-[9px] text-slate-500 font-bold block">EC50 / IC50</span>
                                  <span className="text-sm font-extrabold text-emerald-450 font-mono">
                                    {doseFitResults.ec50.toFixed(4)} µM
                                  </span>
                                </div>

                                <div className="p-2.5 bg-slate-950/40 rounded-xl">
                                  <span className="text-[9px] text-slate-500 font-bold block">Hill Slope</span>
                                  <span className="text-sm font-extrabold text-white font-mono">
                                    {doseFitResults.hill_slope.toFixed(2)}
                                  </span>
                                </div>

                                <div className="p-2.5 bg-slate-950/40 rounded-xl">
                                  <span className="text-[9px] text-slate-500 font-bold block">R² Value</span>
                                  <span className="text-sm font-extrabold text-sky-450 font-mono">
                                    {doseFitResults.r_squared.toFixed(4)}
                                  </span>
                                </div>
                              </div>
                            </div>
                            
                            <div className="text-[10px] text-slate-500 leading-relaxed border-t border-slate-800 pt-3">
                              * Fits regression curve using Least Squares minimization over 4-parameters (Hill Slope, Top, Bottom, EC50).
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="h-full flex justify-center items-center p-10 text-slate-600 font-semibold border border-dashed border-slate-800 rounded-2xl min-h-[300px]">
                          Select concentration and response variable columns and execute fit to plot the dose-response sigmoidal curve.
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
