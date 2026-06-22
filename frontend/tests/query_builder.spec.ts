import { test, expect } from '@playwright/test';

test.describe('Visual Query Builder Workspace', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('http://localhost:5173/login');
    
    // Attempt to log in directly first
    await page.fill('input[placeholder="scientist@company.com"]', 'scientist_e2e@company.com');
    await page.fill('input[placeholder="••••••••"]', 'SecurePassword2026!');
    await page.click('button[type="submit"]');
    
    // If we are still on the login page or see an error, register the user
    await page.waitForTimeout(1000);
    const dashboardHeader = page.locator('h2:has-text("Informatics Hub")');
    if (!(await dashboardHeader.isVisible())) {
      // Toggle to registration form
      const registerToggle = page.locator('button:has-text("Don\'t have an account? Register")');
      if (await registerToggle.isVisible()) {
        await registerToggle.click();
        
        // Fill out registration details
        await page.fill('input[placeholder="Dr. Sarah Jenkins"]', 'Scientist E2E');
        await page.fill('input[placeholder="scientist@company.com"]', 'scientist_e2e@company.com');
        await page.fill('input[placeholder="••••••••"]', 'SecurePassword2026!');
        await page.click('button[type="submit"]');
        
        // Wait and then attempt login again
        await page.waitForTimeout(1000);
        await page.fill('input[placeholder="scientist@company.com"]', 'scientist_e2e@company.com');
        await page.fill('input[placeholder="••••••••"]', 'SecurePassword2026!');
        await page.click('button[type="submit"]');
      }
    }
    
    // Confirm Dashboard loads
    await expect(page.locator('h2:has-text("Informatics Hub")')).toBeVisible();
  });

  test('should insert entity nodes, input filters, and review compiled SQL', async ({ page }) => {
    // Navigate to Visual Query Builder workspace
    await page.click('a:has-text("Query Builder")');
    
    // Verify Workspace layout is visible
    await expect(page.locator('h4:has-text("Query Entities")')).toBeVisible();
    await expect(page.locator('h3:has-text("Trino SQL Preview")')).toBeVisible();

    // Insert Compounds node
    await page.click('button:has-text("Compounds")');
    // Verify Compound node is added to canvas
    await expect(page.locator('.react-flow__node:has-text("COMPOUND")')).toBeVisible();

    // Insert BioAssays node
    await page.click('button:has-text("BioAssays")');
    // Verify Assay node is added to canvas
    await expect(page.locator('.react-flow__node:has-text("ASSAY")')).toBeVisible();

    // Select the first node (Compound) to edit properties
    await page.locator('.react-flow__node:has-text("COMPOUND")').first().click();

    // ConfigPanel should show settings
    await expect(page.locator('h3:has-text("Node Configuration")')).toBeVisible();

    // Click Add Filter button
    await page.click('button:has-text("Add")');
    
    // Edit the filter value
    await page.fill('input[placeholder="Value"]', '450');

    // Delete the BioAssays node to make the graph valid (only one node remaining)
    await page.locator('.react-flow__node:has-text("ASSAY")').first().locator('button[title="Delete Node"]').click();

    // Confirm that the SQL preview reflects the change (compiles a query on compounds)
    await page.waitForTimeout(500);
    const sqlText = await page.locator('pre').innerText();
    expect(sqlText).toContain('SELECT');
    expect(sqlText).toContain('FROM compounds');
    expect(sqlText).toContain('mw');
    expect(sqlText).toContain('450');
  });

  test('should allow saving templates and clearing the workspace canvas', async ({ page }) => {
    await page.click('a:has-text("Query Builder")');
    
    // Add compound node so we have something to compile/save
    await page.click('button:has-text("Compounds")');
    
    // Enter template name
    await page.fill('input[placeholder="Template name..."]', 'E2E Test Template');
    
    // Save template
    await page.click('button:has-text("Save Template")');
    
    // Confirm save text shows "Saved!"
    await expect(page.locator('button:has-text("Saved!")')).toBeVisible();
    
    // Click Clear Canvas
    await page.click('button:has-text("Clear Canvas")');
    
    // Verify nodes are deleted
    await expect(page.locator('.react-flow__node')).toHaveCount(0);
  });
});
