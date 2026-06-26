import { Page, Locator, expect } from '@playwright/test';

export class AuditPage {
  readonly page: Page;
  readonly refreshButton: Locator;
  readonly resetFiltersButton: Locator;
  readonly filterUserSelect: Locator;
  readonly filterServiceSelect: Locator;
  readonly filterActionSelect: Locator;
  
  // Modal details
  readonly detailModalHeader: Locator;
  readonly verifyIntegrityButton: Locator;
  readonly calculatedHashSpan: Locator;
  readonly verificationSuccessAlert: Locator;
  readonly closeButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.refreshButton = page.locator('button:has-text("Refresh Logs")');
    this.resetFiltersButton = page.locator('button:has-text("Reset Filters")');
    this.filterUserSelect = page.locator('label:has-text("Filter by User")').locator('xpath=../select');
    this.filterServiceSelect = page.locator('label:has-text("Filter by Service")').locator('xpath=../select');
    this.filterActionSelect = page.locator('label:has-text("Filter by Action")').locator('xpath=../select');

    // Modal
    this.detailModalHeader = page.locator('span:has-text("Audit Log Record Details")');
    this.verifyIntegrityButton = page.locator('button:has-text("Verify Cryptographic Integrity")');
    this.calculatedHashSpan = page.locator('span:has-text("CALCULATED")');
    this.verificationSuccessAlert = page.locator('p:has-text("Verification Passed"), div:has-text("Integrity Valid")');
    this.closeButton = page.locator('button:has-text("Close"), button:has-text("Dismiss")');
  }

  async navigate() {
    await this.page.goto('/admin/audit');
    await this.refreshButton.waitFor({ state: 'visible' });
  }

  async refresh() {
    await this.refreshButton.click();
    await this.page.waitForTimeout(500);
  }

  async openFirstLogDetails() {
    const detailsBtn = this.page.locator('button:has-text("Details")').first();
    await detailsBtn.waitFor({ state: 'visible', timeout: 5000 });
    await detailsBtn.click();
  }

  async clickVerify() {
    await this.verifyIntegrityButton.first().waitFor({ state: 'visible', timeout: 5000 });
    await this.verifyIntegrityButton.first().click();
  }
}
