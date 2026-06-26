import { Page, Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly secureSessionIndicator: Locator;
  readonly registerToggle: Locator;
  readonly registerNameInput: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('input[placeholder="scientist@company.com"]');
    this.passwordInput = page.locator('input[placeholder="••••••••"]');
    this.submitButton = page.locator('button[type="submit"]');
    this.secureSessionIndicator = page.locator('span:has-text("SECURE SESSION")');
    this.registerToggle = page.locator('button:has-text("Don\'t have an account? Register"), button:has-text("Already have an account? Login")');
    this.registerNameInput = page.locator('input[placeholder="Dr. Sarah Jenkins"]');
  }

  async navigate() {
    await this.page.goto('/login');
    await this.emailInput.waitFor({ state: 'visible' });
  }

  async login(email: string = 'admin@analytix.com', password: string = 'AnalytiXDiscover2026!') {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
    await this.page.waitForURL(/.*dashboard/, { timeout: 30000 });
  }

  async registerAndLogin(name: string, email: string, password: string) {
    // If not already on register form, toggle it
    if (!(await this.registerNameInput.isVisible()) && (await this.registerToggle.isVisible())) {
      await this.registerToggle.click();
    }
    
    await this.registerNameInput.fill(name);
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
    
    // Wait until registration inputs are hidden, indicating login screen is ready
    await this.registerNameInput.waitFor({ state: 'hidden', timeout: 20000 });
    await this.page.waitForTimeout(500);
    
    // Now log in
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
    await this.page.waitForURL(/.*dashboard/, { timeout: 30000 });
  }
}
