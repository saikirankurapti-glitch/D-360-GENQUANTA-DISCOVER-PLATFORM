import { Page, Locator, expect } from '@playwright/test';

export class QueryBuilderPage {
  readonly page: Page;
  readonly queryEntitiesHeader: Locator;
  readonly sqlPreviewHeader: Locator;
  readonly compoundsButton: Locator;
  readonly bioassaysButton: Locator;
  readonly reactFlowNodes: Locator;
  readonly nodeConfigHeader: Locator;
  readonly addFilterButton: Locator;
  readonly filterValueInput: Locator;
  readonly sqlCodeBlock: Locator;
  readonly templateNameInput: Locator;
  readonly saveTemplateButton: Locator;
  readonly clearCanvasButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.queryEntitiesHeader = page.locator('h4:has-text("Query Entities")');
    this.sqlPreviewHeader = page.locator('h3:has-text("Trino SQL Preview")');
    this.compoundsButton = page.locator('button:has-text("Compounds")');
    this.bioassaysButton = page.locator('button:has-text("BioAssays")');
    this.reactFlowNodes = page.locator('.react-flow__node');
    this.nodeConfigHeader = page.locator('h3:has-text("Node Configuration")');
    this.addFilterButton = page.locator('button:has-text("Add")');
    this.filterValueInput = page.locator('input[placeholder="Value"]');
    this.sqlCodeBlock = page.locator('pre');
    this.templateNameInput = page.locator('input[placeholder="Template name..."]');
    this.saveTemplateButton = page.locator('button:has-text("Save Template"), button:has-text("Saved!")');
    this.clearCanvasButton = page.locator('button:has-text("Clear Canvas")');
  }

  async navigate() {
    await this.page.goto('/query-builder');
    await this.compoundsButton.waitFor({ state: 'visible' });
  }

  async addCompoundsNode() {
    await this.compoundsButton.click();
    await this.page.waitForTimeout(200);
  }

  async addBioAssaysNode() {
    await this.bioassaysButton.click();
    await this.page.waitForTimeout(200);
  }

  async selectNode(text: string) {
    await this.reactFlowNodes.filter({ hasText: text }).first().click();
    await this.page.waitForTimeout(200);
  }

  async addFilterRule(value: string) {
    await this.addFilterButton.click();
    await this.filterValueInput.fill(value);
    await this.page.waitForTimeout(200);
  }

  async deleteNode(text: string) {
    const node = this.reactFlowNodes.filter({ hasText: text }).first();
    await node.locator('button[title="Delete Node"]').click();
    await this.page.waitForTimeout(200);
  }

  async getSqlText(): Promise<string> {
    return (await this.sqlCodeBlock.innerText()) || '';
  }

  async saveTemplate(name: string) {
    await this.templateNameInput.fill(name);
    await this.page.click('button:has-text("Save Template")');
    await expect(this.page.locator('button:has-text("Saved!")')).toBeVisible();
  }

  async clearCanvas() {
    await this.clearCanvasButton.click();
    await this.page.waitForTimeout(200);
  }
}
