import { Page, Locator, expect } from '@playwright/test';

export class DashboardPage {
  readonly page: Page;
  readonly seedDbBanner: Locator;
  readonly seedDbButton: Locator;
  readonly chemicalEntitiesCard: Locator;
  readonly bioassaysCard: Locator;
  readonly schemaFieldsCard: Locator;
  readonly ic50Chart: Locator;
  readonly searchMetadataShortcut: Locator;

  constructor(page: Page) {
    this.page = page;
    this.seedDbBanner = page.locator('h3:has-text("Database is unseeded")');
    this.seedDbButton = page.locator('button:has-text("Seed Database")');
    this.chemicalEntitiesCard = page.locator('p:has-text("Chemical Entities")').locator('..');
    this.bioassaysCard = page.locator('p:has-text("BioAssays Registered")').locator('..');
    this.schemaFieldsCard = page.locator('p:has-text("Catalog Schema Fields")').locator('..');
    this.ic50Chart = page.locator('h4:has-text("IC50 Compound Inhibition Profile")').locator('..');
    this.searchMetadataShortcut = page.locator('p:has-text("Search Metadata")').locator('..');
  }

  async navigate() {
    await this.page.goto('/dashboard');
    await this.chemicalEntitiesCard.waitFor({ state: 'visible' });
  }

  async seedDatabaseIfNeeded() {
    await this.page.waitForTimeout(1000);
    if (await this.seedDbButton.isVisible()) {
      await this.seedDbButton.click();
      // Wait for seeding to complete (can take a few seconds)
      await this.page.waitForTimeout(5000);
    }
  }

  async getChemicalEntitiesCount(): Promise<string> {
    const heading = this.chemicalEntitiesCard.locator('h3');
    return (await heading.textContent()) || '';
  }
}
