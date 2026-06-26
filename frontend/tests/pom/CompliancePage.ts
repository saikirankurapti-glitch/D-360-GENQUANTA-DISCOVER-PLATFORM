import { Page, Locator, expect } from '@playwright/test';

export class CompliancePage {
  readonly page: Page;

  // Header & Controls
  readonly titleHeader: Locator;
  readonly refreshButton: Locator;
  readonly verifyDbIntegrityButton: Locator;

  // Tabs
  readonly overviewTab: Locator;
  readonly logsTab: Locator;
  readonly signaturesTab: Locator;
  readonly activityTab: Locator;
  readonly lineageTab: Locator;

  // Overview Panel
  readonly integrityStatusTitle: Locator;
  readonly runVerificationButton: Locator;
  readonly recordsKpi: Locator;
  readonly signaturesKpi: Locator;

  // React Flow Canvas
  readonly reactFlowCanvas: Locator;

  constructor(page: Page) {
    this.page = page;

    // Header
    this.titleHeader = page.locator('h1:has-text("Compliance & Governance Console")');
    this.refreshButton = page.locator('button:has-text("Refresh Data")');
    this.verifyDbIntegrityButton = page.locator('button:has-text("Verify Database Integrity")');

    // Tabs
    this.overviewTab = page.locator('button:has-text("Overview")');
    this.logsTab = page.locator('button:has-text("Cryptographic Logs")');
    this.signaturesTab = page.locator('button:has-text("E-Signatures")');
    this.activityTab = page.locator('button:has-text("User Activity")');
    this.lineageTab = page.locator('button:has-text("Data Lineage")');

    // Overview Tab Content
    this.integrityStatusTitle = page.locator('h3:has-text("Verification Status"), h3:has-text("Ledger")');
    this.runVerificationButton = page.locator('button:has-text("Run Verification")');
    this.recordsKpi = page.locator('h4:has-text("Audit Trail Records")').locator('..');
    this.signaturesKpi = page.locator('h4:has-text("Electronic Signatures")').locator('..');

    // React Flow Canvas in Lineage
    this.reactFlowCanvas = page.locator('.react-flow__viewport');
  }

  async navigate() {
    await this.page.goto('/compliance');
    await this.titleHeader.waitFor({ state: 'visible' });
  }

  async selectTab(tab: 'overview' | 'logs' | 'signatures' | 'activity' | 'lineage') {
    if (tab === 'overview') await this.overviewTab.click();
    else if (tab === 'logs') await this.logsTab.click();
    else if (tab === 'signatures') await this.signaturesTab.click();
    else if (tab === 'activity') await this.activityTab.click();
    else if (tab === 'lineage') await this.lineageTab.click();
    await this.page.waitForTimeout(500);
  }

  async triggerLedgerVerify() {
    await this.verifyDbIntegrityButton.click();
    await this.page.waitForTimeout(2000);
  }
}
