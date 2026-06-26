import { Page, Locator, expect } from '@playwright/test';

export class WorkflowPage {
  readonly page: Page;

  // Toolbar & Header
  readonly definitionSelect: Locator;
  readonly workflowNameInput: Locator;
  readonly workflowDescInput: Locator;
  readonly saveWorkflowButton: Locator;
  readonly runWorkflowButton: Locator;

  // Left panel (Nodes)
  readonly nodeButtons: Record<string, Locator>;

  // React Flow Canvas
  readonly reactFlowCanvas: Locator;
  readonly flowNodes: Locator;

  // Right sidebar & tabs
  readonly settingsTabButton: Locator;
  readonly historyTabButton: Locator;
  readonly signaturesTabButton: Locator;
  readonly metricsTabButton: Locator;

  // settings configuration
  readonly stepNameInput: Locator;
  readonly sqlScriptTextArea: Locator;
  readonly smilesInput: Locator;
  readonly recipientInput: Locator;

  // approvals / signatures
  readonly pendingSignaturesHeader: Locator;
  readonly signatureApproverInput: Locator;
  readonly signatureCommentInput: Locator;
  readonly signaturePasswordInput: Locator;
  readonly approveButton: Locator;
  readonly signatureStatusMessage: Locator;

  // History details
  readonly runsList: Locator;
  readonly detailBackButton: Locator;
  readonly runStatusBadge: Locator;

  constructor(page: Page) {
    this.page = page;

    // Header Toolbar
    this.definitionSelect = page.locator('select').first();
    this.workflowNameInput = page.locator('input[placeholder="Workflow Name..."]');
    this.workflowDescInput = page.locator('input[placeholder="Description..."]');
    this.saveWorkflowButton = page.locator('button:has-text("Save Workflow")');
    this.runWorkflowButton = page.locator('button:has-text("Run Workflow")');

    // Left Node panel
    this.nodeButtons = {
      datasource: page.locator('button:has-text("Data Ingest")'),
      sync: page.locator('button:has-text("Catalog Sync")'),
      query: page.locator('button:has-text("Trino SQL Query")'),
      compound_search: page.locator('button:has-text("Molecular Search")'),
      sequence_analysis: page.locator('button:has-text("Bioinfo Alignment")'),
      assay_analysis: page.locator('button:has-text("Assay Curve Fitting")'),
      export: page.locator('button:has-text("CSV Exporter")'),
      notification: page.locator('button:has-text("Dispatch Alert")'),
      approval: page.locator('button:has-text("Signature Approval Gate")'),
    };

    // Canvas
    this.reactFlowCanvas = page.locator('.react-flow__viewport');
    this.flowNodes = page.locator('.react-flow__node');

    // Right Sidebar
    this.settingsTabButton = page.locator('button:has-text("Settings")');
    this.historyTabButton = page.locator('button:has-text("History")');
    this.signaturesTabButton = page.locator('button:has-text("Signatures")');
    this.metricsTabButton = page.locator('button:has-text("Metrics")');

    // Node Settings
    this.stepNameInput = page.locator('label:has-text("Step Name")').locator('xpath=../input');
    this.sqlScriptTextArea = page.locator('textarea');
    this.smilesInput = page.locator('input[placeholder*="SMILES String"], label:has-text("SMILES String")').locator('xpath=../input');
    this.recipientInput = page.locator('input[type="email"]');

    // Signatures / FDA Part 11
    this.pendingSignaturesHeader = page.locator('h5:has-text("Pending Electronic Signatures")');
    this.signatureApproverInput = page.locator('input[placeholder="Approver Fullname"]');
    this.signatureCommentInput = page.locator('input[placeholder="Approval comment..."]');
    this.signaturePasswordInput = page.locator('input[placeholder="Password PIN verification"]');
    this.approveButton = page.locator('button:has-text("Approve / Verify")');
    this.signatureStatusMessage = page.locator('div:has-text("Signature stored and verified")');

    // Runs list & details
    this.runsList = page.locator('h5:has-text("Run Details")').locator('xpath=..');
    this.detailBackButton = page.locator('button:has-text("Back to List")');
    this.runStatusBadge = page.locator('span.font-mono').first();
  }

  async navigate() {
    await this.page.goto('/workflows');
    await this.runWorkflowButton.waitFor({ state: 'visible' });
  }

  async addNode(type: 'datasource' | 'sync' | 'query' | 'compound_search' | 'sequence_analysis' | 'assay_analysis' | 'export' | 'notification' | 'approval') {
    const btn = this.nodeButtons[type];
    await btn.click();
    await this.page.waitForTimeout(500);
  }

  async selectNode(text: string) {
    const node = this.flowNodes.filter({ hasText: text }).first();
    await node.click();
    await this.page.waitForTimeout(200);
  }

  async configureQueryNode(sql: string) {
    await this.sqlScriptTextArea.fill(sql);
    await this.page.waitForTimeout(200);
  }

  async saveWorkflow(name: string, desc: string) {
    await this.workflowNameInput.fill(name);
    await this.workflowDescInput.fill(desc);
    await this.saveWorkflowButton.click();
    await this.page.waitForTimeout(1000);
  }

  async triggerWorkflowRun() {
    await this.runWorkflowButton.click();
    await this.page.waitForTimeout(1500);
  }

  async signApproval(approver: string, comment: string, pin: string) {
    await this.signaturesTabButton.click();
    await this.page.waitForTimeout(500);
    if (await this.signatureApproverInput.isVisible()) {
      await this.signatureApproverInput.fill(approver);
      await this.signatureCommentInput.fill(comment);
      await this.signaturePasswordInput.fill(pin);
      await this.approveButton.click();
      await this.page.waitForTimeout(1500);
    }
  }
}
