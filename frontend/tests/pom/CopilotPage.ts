import { Page, Locator, expect } from '@playwright/test';

export class CopilotPage {
  readonly page: Page;

  // Sessions sidebar
  readonly createSessionButton: Locator;
  readonly sessionItems: Locator;

  // Chat panel
  readonly chatInput: Locator;
  readonly sendButton: Locator;
  readonly messageItems: Locator;

  // Tabs on display panel
  readonly planTabButton: Locator;
  readonly dashboardTabButton: Locator;
  readonly workflowTabButton: Locator;

  // Tab Contents
  readonly explanationHeader: Locator;
  readonly planSteps: Locator;
  readonly deployWorkflowButton: Locator;
  readonly noQueryPlanHeader: Locator;

  constructor(page: Page) {
    this.page = page;

    // Sidebar
    this.createSessionButton = page.locator('button[title="Start New Discussion"]');
    this.sessionItems = page.locator('aside button');

    // Chat
    this.chatInput = page.locator('textarea[placeholder*="Ask the AI Scientist"], input[placeholder*="scientific"], input[type="text"]').first();
    this.sendButton = page.locator('input[placeholder*="scientific"] ~ button, textarea ~ button, button:has(svg.lucide-send)').first();
    this.messageItems = page.locator('.message, [class*="message"]');

    // Display Tabs
    this.planTabButton = page.locator('button:has-text("Query Plan & SQL")');
    this.dashboardTabButton = page.locator('button:has-text("AI Dashboard")');
    this.workflowTabButton = page.locator('button:has-text("AI Workflow")');

    // Contents
    this.explanationHeader = page.locator('span:has-text("Federated Query Explanation")');
    this.planSteps = page.locator('div:has-text("Plan Execution Trace")').locator('..');
    this.deployWorkflowButton = page.locator('button:has-text("Deploy Workflow")');
    this.noQueryPlanHeader = page.locator('h4:has-text("No Query Plan Compiled")');
  }

  async navigate() {
    await this.page.goto('/copilot');
    await this.chatInput.waitFor({ state: 'visible' });
  }

  async selectTab(tab: 'plan' | 'dashboard' | 'workflow') {
    if (tab === 'plan') await this.planTabButton.click();
    else if (tab === 'dashboard') await this.dashboardTabButton.click();
    else if (tab === 'workflow') await this.workflowTabButton.click();
    await this.page.waitForTimeout(500);
  }

  async startNewDiscussion() {
    if (await this.createSessionButton.isVisible()) {
      await this.createSessionButton.click();
      await this.page.waitForTimeout(500);
    }
  }

  async submitMessage(msg: string) {
    await this.chatInput.fill(msg);
    await this.sendButton.click();
    await this.page.waitForTimeout(2000); // wait for AI response
  }
}
