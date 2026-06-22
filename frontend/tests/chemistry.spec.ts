import { test, expect } from '@playwright/test';

test.describe('Cheminformatics & SAR Workspace', () => {
  
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

  test('should load Compound Explorer interface and allow structure pasting', async ({ page }) => {
    // Click Compound Explorer nav link
    await page.click('a:has-text("Compound Explorer")');
    
    // Verify Page Header and layout panels are visible
    await expect(page.locator('h2:has-text("Compound Explorer")')).toBeVisible();
    await expect(page.locator('h4:has-text("Structure Query")')).toBeVisible();
    await expect(page.locator('h4:has-text("Search Parameters")')).toBeVisible();

    // Fill in a SMILES structure query
    await page.fill('input[placeholder="Paste SMILES (e.g. C1=CC=CC=C1)..."]', 'CC(=O)Oc1ccccc1C(=O)O');
    
    // Select Similarity Search
    await page.selectOption('select', 'similarity');
    
    // Verify that the similarity threshold slider appears
    await expect(page.locator('span:has-text("Similarity Threshold")')).toBeVisible();
  });

  test('should load SAR Decomposition workspace and show analogue items', async ({ page }) => {
    // Click SAR Decomposition nav link
    await page.click('a:has-text("SAR Decomposition")');
    
    // Verify Page Header and scaffold inputs
    await expect(page.locator('h2:has-text("SAR Decomposition")')).toBeVisible();
    await expect(page.locator('h4:has-text("Core Scaffold Scaffold")')).toBeVisible();
    await expect(page.locator('h3:has-text("Target Compounds Analogue Activity")')).toBeVisible();

    // Verify seed compounds list is present
    await expect(page.locator('span:has-text("Toluene")')).toBeVisible();
    await expect(page.locator('span:has-text("Phenol")')).toBeVisible();
    
    // Verify Decompose button is present
    await expect(page.locator('button:has-text("Decompose Scaffold")')).toBeVisible();
  });
});
