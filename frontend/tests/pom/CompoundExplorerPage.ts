import { Page, Locator, expect } from '@playwright/test';

export class CompoundExplorerPage {
  readonly page: Page;

  // Compound Explorer selectors
  readonly queryHeader: Locator;
  readonly paramsHeader: Locator;
  readonly smilesInput: Locator;
  readonly searchModeSelect: Locator;
  readonly similarityThresholdSlider: Locator;
  readonly executeSearchButton: Locator;
  readonly resultsGrid: Locator;

  // SAR Decomposition selectors
  readonly sarHeader: Locator;
  readonly scaffoldInputHeader: Locator;
  readonly seedCompoundToluene: Locator;
  readonly seedCompoundPhenol: Locator;
  readonly decomposeButton: Locator;

  constructor(page: Page) {
    this.page = page;

    // Explorer
    this.queryHeader = page.locator('h4:has-text("Structure Query")');
    this.paramsHeader = page.locator('h4:has-text("Search Parameters")');
    this.smilesInput = page.locator('input[placeholder="Paste SMILES (e.g. C1=CC=CC=C1)..."]');
    this.searchModeSelect = page.locator('select');
    this.similarityThresholdSlider = page.locator('span:has-text("Similarity Threshold")');
    this.executeSearchButton = page.locator('button:has-text("Search")');
    this.resultsGrid = page.locator('.ag-theme-quartz-dark');

    // SAR
    this.sarHeader = page.locator('h2:has-text("SAR Decomposition")');
    this.scaffoldInputHeader = page.locator('h4:has-text("Core Scaffold Scaffold")');
    this.seedCompoundToluene = page.locator('span:has-text("Toluene")');
    this.seedCompoundPhenol = page.locator('span:has-text("Phenol")');
    this.decomposeButton = page.locator('button:has-text("Decompose Scaffold")');
  }

  async navigateExplorer() {
    await this.page.goto('/compounds');
    await this.smilesInput.waitFor({ state: 'visible' });
  }

  async navigateSar() {
    await this.page.goto('/sar');
    await this.decomposeButton.waitFor({ state: 'visible' });
  }

  async fillSmiles(smiles: string) {
    await this.smilesInput.fill(smiles);
    await this.page.waitForTimeout(200);
  }

  async selectSearchMode(mode: 'exact' | 'substructure' | 'similarity') {
    await this.searchModeSelect.selectOption(mode);
    await this.page.waitForTimeout(200);
  }

  async triggerDecompose() {
    // Click Benzene preset button to populate scaffold SMILES
    await this.page.locator('button:has-text("Benzene")').first().click();
    await this.decomposeButton.click();
    await this.page.waitForTimeout(1000);
  }
}
