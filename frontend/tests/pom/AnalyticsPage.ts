import { Page, Locator, expect } from '@playwright/test';

export class AnalyticsPage {
  readonly page: Page;

  // Header & Global Buttons
  readonly titleHeader: Locator;
  readonly loadDemoButton: Locator;
  
  // Sidebar items
  readonly querySourceSelect: Locator;
  readonly workspaceNameInput: Locator;
  readonly saveWorkspaceButton: Locator;

  // Tabs
  readonly dataGridTabButton: Locator;
  readonly plotsTabButton: Locator;
  readonly pcaTabButton: Locator;
  readonly clusteringTabButton: Locator;
  readonly correlationTabButton: Locator;
  readonly doseResponseTabButton: Locator;

  // PCA controls & results
  readonly executePcaButton: Locator;
  readonly pcaExplainedVariance: Locator;
  readonly pcaLoadingIndicator: Locator;

  // Clustering controls & results
  readonly executeClusteringButton: Locator;
  readonly clusterAlgorithmSelect: Locator;
  readonly nClustersInput: Locator;

  // Dose-response controls & results
  readonly concentrationSelect: Locator;
  readonly responseSelect: Locator;
  readonly executeDoseFitButton: Locator;
  readonly ic50ResultDiv: Locator;

  constructor(page: Page) {
    this.page = page;

    // Header & Global
    this.titleHeader = page.locator('h1:has-text("Scientific Analytics Workbench")');
    this.loadDemoButton = page.locator('button:has-text("Load Demo Dataset")');

    // Sidebar
    this.querySourceSelect = page.locator('select').first();
    this.workspaceNameInput = page.locator('input[placeholder="Workspace Name..."]');
    this.saveWorkspaceButton = page.locator('button:has-text("Save Current Workspace")');

    // Tabs
    this.dataGridTabButton = page.locator('button:has-text("Data Grid")');
    this.plotsTabButton = page.locator('button:has-text("Exploratory Plots")');
    this.pcaTabButton = page.locator('button:has-text("PCA / t-SNE Map")');
    this.clusteringTabButton = page.locator('button:has-text("Clustering")');
    this.correlationTabButton = page.locator('button:has-text("Correlation Heatmap")');
    this.doseResponseTabButton = page.locator('button:has-text("Dose-Response (IC50)")');

    // PCA
    this.executePcaButton = page.locator('button:has-text("Run PCA Reduction"), button:has-text("Run PCA")');
    this.pcaExplainedVariance = page.locator('h5:has-text("Explained Variance Ratio")');
    this.pcaLoadingIndicator = page.locator('span:has-text("Computing PCA...")');

    // Clustering
    this.executeClusteringButton = page.locator('button:has-text("Run Clustering"), button:has-text("Run Clustering Analysis")');
    this.clusterAlgorithmSelect = page.locator('select').nth(1); // after query source select
    this.nClustersInput = page.locator('input[type="number"]');

    // Dose Response
    this.concentrationSelect = page.locator('select[value*="concentration"], select').nth(1);
    this.responseSelect = page.locator('select[value*="inhibition"], select').nth(2);
    this.executeDoseFitButton = page.locator('button:has-text("Calculate Dose-Response Fit"), button:has-text("Fit Dose-Response"), button:has-text("Fit Sigmoidal Curve")');
    this.ic50ResultDiv = page.locator('h4:has-text("Fit Outputs")');
  }

  async navigate() {
    await this.page.goto('/analytics-workbench');
    await this.titleHeader.waitFor({ state: 'visible' });
  }

  async loadDemoDataset() {
    await this.loadDemoButton.click();
    await this.page.waitForTimeout(500);
  }

  async selectTab(tab: 'grid' | 'plots' | 'pca' | 'clustering' | 'correlation' | 'doseresp') {
    if (tab === 'grid') await this.dataGridTabButton.click();
    else if (tab === 'plots') await this.plotsTabButton.click();
    else if (tab === 'pca') await this.pcaTabButton.click();
    else if (tab === 'clustering') await this.clusteringTabButton.click();
    else if (tab === 'correlation') await this.correlationTabButton.click();
    else if (tab === 'doseresp') await this.doseResponseTabButton.click();
    await this.page.waitForTimeout(500);
  }
}
