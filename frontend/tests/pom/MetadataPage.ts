import { Page, Locator, expect } from '@playwright/test';

export class MetadataPage {
  readonly page: Page;
  readonly catalogTabButton: Locator;
  readonly explorerTabButton: Locator;
  readonly relationshipsTabButton: Locator;
  readonly historyTabButton: Locator;
  
  // Catalog Registry tab
  readonly searchInput: Locator;
  readonly typeFilter: Locator;
  readonly refreshButton: Locator;
  readonly agGridTable: Locator;
  readonly registryHeader: Locator;

  // Schema & Lineage tab
  readonly schemaEntitiesList: Locator;
  readonly selectedEntityHeader: Locator;
  readonly lineageCanvas: Locator;
  readonly schemaFieldsTable: Locator;

  // Relationship Map tab
  readonly relationshipMapHeader: Locator;
  readonly joinIndicators: Locator;

  // Audit & Timeline tab
  readonly syncNowButton: Locator;
  readonly syncLogTable: Locator;
  readonly timelineItems: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // Tabs
    this.catalogTabButton = page.locator('button:has-text("Catalog Registry")');
    this.explorerTabButton = page.locator('button:has-text("Schema & Lineage")');
    this.relationshipsTabButton = page.locator('button:has-text("Relationship Map")');
    this.historyTabButton = page.locator('button:has-text("Audit & Timeline")');

    // Catalog
    this.searchInput = page.locator('input[placeholder="Search key, name, properties, or SMILES..."]');
    this.typeFilter = page.locator('select');
    this.refreshButton = page.locator('button:has-text("Refresh")');
    this.agGridTable = page.locator('.ag-theme-quartz-dark');
    this.registryHeader = page.locator('span:has-text("Entity Registry")');

    // Schema & Lineage
    this.schemaEntitiesList = page.locator('h3:has-text("Registered Schema Entities")').locator('xpath=..');
    this.selectedEntityHeader = page.locator('span:has-text("Lineage / Resource Key")').locator('xpath=..');
    this.lineageCanvas = page.locator('span:has-text("Lineage Origin")').locator('xpath=..');
    this.schemaFieldsTable = page.locator('h4:has-text("Schema Fields")').locator('xpath=..').locator('table');

    // Relationships
    this.relationshipMapHeader = page.locator('h3:has-text("Dynamic Entity Relationship Graph")');
    this.joinIndicators = page.locator('span:has-text("JOIN")');

    // History
    this.syncNowButton = page.locator('button:has-text("Sync Now")');
    this.syncLogTable = page.locator('h4:has-text("Federation Sync Log")').locator('..').locator('table');
    this.timelineItems = page.locator('h4:has-text("Schema Version Timeline")').locator('..').locator('.relative');
  }

  async navigate() {
    await this.page.goto('/metadata');
    await this.catalogTabButton.waitFor({ state: 'visible' });
  }

  async selectTab(tab: 'catalog' | 'explorer' | 'relationships' | 'history') {
    if (tab === 'catalog') await this.catalogTabButton.click();
    else if (tab === 'explorer') await this.explorerTabButton.click();
    else if (tab === 'relationships') await this.relationshipsTabButton.click();
    else if (tab === 'history') await this.historyTabButton.click();
    await this.page.waitForTimeout(500);
  }

  async searchCatalog(text: string) {
    await this.searchInput.fill(text);
    await this.page.waitForTimeout(500);
  }

  async triggerManualSync() {
    if (await this.syncNowButton.first().isVisible()) {
      await this.syncNowButton.first().click();
      await this.page.waitForTimeout(3050); // wait for sync to finish
    }
  }
}
