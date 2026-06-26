import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { LoginPage } from './pom/LoginPage';
import { DashboardPage } from './pom/DashboardPage';
import { MetadataPage } from './pom/MetadataPage';
import { QueryBuilderPage } from './pom/QueryBuilderPage';
import { CompoundExplorerPage } from './pom/CompoundExplorerPage';
import { BioinformaticsPage } from './pom/BioinformaticsPage';
import { AnalyticsPage } from './pom/AnalyticsPage';
import { WorkflowPage } from './pom/WorkflowPage';
import { AuditPage } from './pom/AuditPage';
import { CompliancePage } from './pom/CompliancePage';
import { CopilotPage } from './pom/CopilotPage';

import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

interface ModuleResult {
  moduleName: string;
  status: 'Pass' | 'Fail';
  executionTimeMs: number;
  screenshotPath: string;
  errorMessage?: string;
}

const testResults: ModuleResult[] = [];
const reportsDir = path.resolve(__dirname, '../../reports');
const screenshotDir = path.resolve(reportsDir, 'screenshots');


test.describe('AnalytiX Platform E2E UI Verification Suite', () => {
  
  test.beforeAll(() => {
    // Ensure reporting directories exist
    if (!fs.existsSync(reportsDir)) fs.mkdirSync(reportsDir, { recursive: true });
    if (!fs.existsSync(screenshotDir)) fs.mkdirSync(screenshotDir, { recursive: true });
  });

  test.afterAll(() => {
    // Write UI execution results to a standardized JSON file
    const uiResultsPath = path.join(reportsDir, 'ui_results.json');
    fs.writeFileSync(uiResultsPath, JSON.stringify(testResults, null, 2));
    console.log(`Saved UI results to: ${uiResultsPath}`);
  });

  async function runModule(
    moduleName: string,
    page: any,
    testFn: () => Promise<void>
  ) {
    const startTime = Date.now();
    const cleanModuleName = moduleName.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
    const screenshotPath = path.join(screenshotDir, `${cleanModuleName}.png`);
    
    try {
      console.log(`[START] Verification for module: ${moduleName}`);
      page.on('dialog', async (dialog: any) => {
        console.log(`[DIALOG] Auto-accepting dialog: "${dialog.message()}"`);
        await dialog.accept();
      });
      await testFn();
      const duration = Date.now() - startTime;
      
      // Capture success screenshot
      await page.screenshot({ path: screenshotPath, fullPage: false });
      
      testResults.push({
        moduleName,
        status: 'Pass',
        executionTimeMs: duration,
        screenshotPath: path.relative(path.join(__dirname, '../..'), screenshotPath).replace(/\\/g, '/'),
      });
      console.log(`[PASS] ${moduleName} - ${duration}ms`);
    } catch (err: any) {
      const duration = Date.now() - startTime;
      const failScreenshotPath = path.join(screenshotDir, `${cleanModuleName}_fail.png`);
      
      // Capture failure screenshot
      await page.screenshot({ path: failScreenshotPath, fullPage: false });
      
      testResults.push({
        moduleName,
        status: 'Fail',
        executionTimeMs: duration,
        screenshotPath: path.relative(path.join(__dirname, '../..'), failScreenshotPath).replace(/\\/g, '/'),
        errorMessage: err.message || String(err),
      });
      console.error(`[FAIL] ${moduleName} - Error: ${err.message || err}`);
      throw err;
    }
  }

  test('Module 1: Authentication & Secure Session', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await runModule('Login & Authentication', page, async () => {
      await loginPage.navigate();
      
      // Attempt login with default admin credentials
      await loginPage.login();
      
      // We should be redirected to dashboard
      await expect(page).toHaveURL(/.*dashboard/);

      // Check for security indicators in the sidebar layout post-login
      await expect(loginPage.secureSessionIndicator).toBeVisible();
    });
  });

  test('Module 2: Dashboard Overview & DB Seeding', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);
    
    await runModule('Dashboard Hub', page, async () => {
      await loginPage.navigate();
      await loginPage.login();
      
      await dashboardPage.navigate();
      
      // If database is unseeded, seed it
      await dashboardPage.seedDatabaseIfNeeded();
      
      // Verify statistics cards are visible
      await expect(dashboardPage.chemicalEntitiesCard).toBeVisible();
      await expect(dashboardPage.bioassaysCard).toBeVisible();
      await expect(dashboardPage.schemaFieldsCard).toBeVisible();
      
      // Verify the interactive IC50 inhibition SVG chart loads
      await expect(dashboardPage.ic50Chart).toBeVisible();
    });
  });

  test('Module 3: Data Registry Catalog', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const metadataPage = new MetadataPage(page);
    
    await runModule('Data Registry', page, async () => {
      await loginPage.navigate();
      await loginPage.login();
      
      await metadataPage.navigate();
      await metadataPage.selectTab('catalog');
      
      // Verify registry header
      await expect(metadataPage.registryHeader).toBeVisible();
      
      // Verify AG Grid catalog table
      await expect(metadataPage.agGridTable).toBeVisible();
      
      // Run a filter search
      await metadataPage.searchCatalog('CMP-001');
    });
  });

  test('Module 4: Metadata Catalog Fields', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const metadataPage = new MetadataPage(page);
    
    await runModule('Metadata Catalog', page, async () => {
      await loginPage.navigate();
      await loginPage.login();
      
      await metadataPage.navigate();
      await metadataPage.selectTab('explorer');
      
      // Verify metadata schema details
      await expect(metadataPage.schemaEntitiesList).toBeVisible();
      
      // Select the first entity in the list and inspect fields
      const firstEntityBtn = metadataPage.schemaEntitiesList.locator('button').first();
      if (await firstEntityBtn.isVisible()) {
        await firstEntityBtn.click();
        await expect(metadataPage.schemaFieldsTable).toBeVisible();
      }
    });
  });

  test('Module 5: Query Builder Workspace', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const queryBuilder = new QueryBuilderPage(page);
    
    await runModule('Query Builder', page, async () => {
      await loginPage.navigate();
      await loginPage.login();
      
      await queryBuilder.navigate();
      await expect(queryBuilder.queryEntitiesHeader).toBeVisible();
      
      // Add nodes to visual canvas
      await queryBuilder.addCompoundsNode();
      await queryBuilder.addBioAssaysNode();
      
      // Verify react flow nodes are added
      await expect(queryBuilder.reactFlowNodes).toHaveCount(2);
      
      // Verify Trino SQL Preview generates appropriate JOIN query
      const sqlText = await queryBuilder.getSqlText();
      expect(sqlText).toContain('SELECT');
      expect(sqlText).toContain('JOIN');
    });
  });

  test('Module 6: Compound Explorer & SAR Search', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const compoundExplorer = new CompoundExplorerPage(page);
    
    await runModule('Compound Explorer', page, async () => {
      await loginPage.navigate();
      await loginPage.login();
      
      // Test Structure Similarity Search
      await compoundExplorer.navigateExplorer();
      await expect(compoundExplorer.queryHeader).toBeVisible();
      
      // Fill Smiles and run similarity search
      await compoundExplorer.fillSmiles('C1=CC=CC=C1');
      await compoundExplorer.selectSearchMode('similarity');
      await compoundExplorer.executeSearchButton.click();
      
      await expect(compoundExplorer.resultsGrid).toBeVisible();
      
      // Test SAR Scaffold Decomposition
      await compoundExplorer.navigateSar();
      await expect(compoundExplorer.sarHeader).toBeVisible();
      await compoundExplorer.triggerDecompose();
    });
  });

  test('Module 7: Bioinformatics Explorer Hub', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const bioPage = new BioinformaticsPage(page);
    
    await runModule('Bioinformatics Explorer', page, async () => {
      await loginPage.navigate();
      await loginPage.login();
      
      // Verify BioHub Dashboard
      await bioPage.navigateHub();
      await expect(bioPage.biohubHeader).toBeVisible();
      
      // Verify Sequence Explorer & parameters calculation
      await bioPage.navigateSequences();
      const fastaData = `>Seq_Test_1 insulin segment\nMALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN`;
      await bioPage.importFasta(fastaData);
      await expect(bioPage.seqBlockContainer).toBeVisible();
      
      // Verify Pairwise Alignments
      await bioPage.navigateAlignments();
      await bioPage.performPairwiseAlignment();
      await expect(bioPage.alignmentOutputScore).toBeVisible();
    });
  });

  test('Module 8: Analytics Workbench Calculations', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const analytics = new AnalyticsPage(page);
    
    await runModule('Analytics Workbench', page, async () => {
      await loginPage.navigate();
      await loginPage.login();
      
      await analytics.navigate();
      await expect(analytics.titleHeader).toBeVisible();
      
      // Load Demo Dataset
      await analytics.loadDemoDataset();
      
      // Switch tabs and verify Plotly curves are rendered
      await analytics.selectTab('doseresp');
      await analytics.executeDoseFitButton.click();
      await expect(analytics.ic50ResultDiv).toBeVisible({ timeout: 20000 });
    });
  });

  test('Module 9: Workflow Automation Pipeline', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const workflow = new WorkflowPage(page);
    
    await runModule('Workflow Automation', page, async () => {
      await loginPage.navigate();
      await loginPage.login();
      
      await workflow.navigate();
      
      // Add multiple nodes to the visual editor
      await workflow.addNode('datasource');
      await workflow.addNode('query');
      
      // Select Query node and write SQL script
      await workflow.selectNode('query');
      await workflow.configureQueryNode('SELECT * FROM metadata.metadata_entities LIMIT 10;');
      
      // Save Workflow
      await workflow.saveWorkflow('E2E Test Sync Pipeline', 'Verifying workflow save/load E2E UI actions');
      
      // Trigger execution run
      await workflow.triggerWorkflowRun();
    });
  });

  test('Module 10: FDA Part 11 Audit Trail Verification', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const audit = new AuditPage(page);
    
    await runModule('Audit Trail Logs', page, async () => {
      await loginPage.navigate();
      await loginPage.login();
      
      await audit.navigate();
      await audit.refresh();
      
      // Open verification modal for the first log entry
      await audit.openFirstLogDetails();
      await audit.clickVerify();
      
      // Assert cryptographic integrity success
      await expect(audit.verificationSuccessAlert).toBeVisible();
      await audit.closeButton.first().click();
    });
  });

  test('Module 11: Compliance Console Overview', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const compliance = new CompliancePage(page);
    
    await runModule('Compliance Console', page, async () => {
      await loginPage.navigate();
      await loginPage.login();
      
      await compliance.navigate();
      await expect(compliance.titleHeader).toBeVisible();
      
      // Perform ledger verification
      await compliance.triggerLedgerVerify();
      await expect(compliance.integrityStatusTitle).toBeVisible();
    });
  });

  test('Module 12: Data Lineage Graph', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const compliance = new CompliancePage(page);
    
    await runModule('Data Lineage Explorer', page, async () => {
      await loginPage.navigate();
      await loginPage.login();
      
      await compliance.navigate();
      await compliance.selectTab('lineage');
      
      // Verify visual React Flow representation is rendered
      await expect(compliance.reactFlowCanvas).toBeVisible();
    });
  });

  test('Module 13: AI Scientist Copilot Panel', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const copilot = new CopilotPage(page);
    
    await runModule('AI Scientist Copilot', page, async () => {
      await loginPage.navigate();
      await loginPage.login();
      
      await copilot.navigate();
      
      // Verify Chat & New Discussion
      await copilot.startNewDiscussion();
      await copilot.submitMessage('Identify active compounds inhibiting EGFR');
      
      // Query Plan tab should compile automatically
      await copilot.selectTab('plan');
      await expect(copilot.explanationHeader).toBeVisible({ timeout: 25000 });
    });
  });

  test('Module 14: User Administration Registry', async ({ page }) => {
    const loginPage = new LoginPage(page);
    
    await runModule('User Administration', page, async () => {
      // Navigate to Login, register a new scientist profile, and verify secure access
      await loginPage.navigate();
      const uniqueEmail = `scientist_${Date.now()}@quantaa.com`;
      await loginPage.registerAndLogin('Dr. Alex Carter', uniqueEmail, 'DiscoverySafetyPIN2026!');
      
      // Verify redirection to dashboard as authenticated user
      await expect(page).toHaveURL(/.*dashboard/);
    });
  });

});
