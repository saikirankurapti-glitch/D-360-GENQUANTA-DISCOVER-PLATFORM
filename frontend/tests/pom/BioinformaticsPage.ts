import { Page, Locator, expect } from '@playwright/test';

export class BioinformaticsPage {
  readonly page: Page;

  // Bioinformatics Hub Dashboard
  readonly biohubHeader: Locator;
  readonly sequenceExplorerCard: Locator;
  readonly alignmentStudioCard: Locator;
  readonly clusteringCenterCard: Locator;

  // Sequence Explorer
  readonly fastaTextArea: Locator;
  readonly runFastaImportButton: Locator;
  readonly importStatusMessage: Locator;
  readonly sequenceCatalogList: Locator;
  readonly seqBlockContainer: Locator;
  readonly molWeightDiv: Locator;

  // Alignment Studio
  readonly pairwiseTabButton: Locator;
  readonly msaTabButton: Locator;
  readonly selectSeqA: Locator;
  readonly selectSeqB: Locator;
  readonly calculateAlignmentButton: Locator;
  readonly alignmentOutputScore: Locator;
  readonly alignmentStringView: Locator;

  // Clustering Center
  readonly clusteringMethodSelect: Locator;
  readonly runClusteringButton: Locator;
  readonly plotlyDendrogram: Locator;

  constructor(page: Page) {
    this.page = page;

    // Dashboard
    this.biohubHeader = page.locator('h1:has-text("Biology & Bioinformatics Platform")');
    this.sequenceExplorerCard = page.locator('h3:has-text("Sequence Explorer")');
    this.alignmentStudioCard = page.locator('h3:has-text("Sequence Alignment Studio")');
    this.clusteringCenterCard = page.locator('h3:has-text("Sequence Clustering Center")');

    // Sequence Explorer
    this.fastaTextArea = page.locator('textarea[placeholder*="ATGCTAGCTAGC"]');
    this.runFastaImportButton = page.locator('button:has-text("Run FASTA Import")');
    this.importStatusMessage = page.locator('form button').locator('xpath=../div[contains(@class, "rounded-lg")]');
    this.sequenceCatalogList = page.locator('h3:has-text("Sequence Catalog")').locator('..');
    this.seqBlockContainer = page.locator('h4:has-text("Sequence Block")').locator('..').locator('.font-mono');
    this.molWeightDiv = page.locator('div:has-text("Molecular Weight")').locator('..');

    // Alignment Studio
    this.pairwiseTabButton = page.locator('button:has-text("Pairwise Sequence Alignment")');
    this.msaTabButton = page.locator('button:has-text("Multiple Sequence Alignment")');
    this.selectSeqA = page.locator('label:has-text("Sequence A")').locator('xpath=../select');
    this.selectSeqB = page.locator('label:has-text("Sequence B")').locator('xpath=../select');
    this.calculateAlignmentButton = page.locator('button:has-text("Calculate Alignment")');
    this.alignmentOutputScore = page.locator('span:has-text("Score:")');
    this.alignmentStringView = page.locator('h4:has-text("Alignment String View")').locator('..').locator('.font-mono');

    // Clustering Center
    this.clusteringMethodSelect = page.locator('select');
    this.runClusteringButton = page.locator('button:has-text("Run Clustering Analysis")');
    this.plotlyDendrogram = page.locator('.js-plotly-plot');
  }

  async navigateHub() {
    await this.page.goto('/bioinformatics');
    await this.biohubHeader.waitFor({ state: 'visible' });
  }

  async navigateSequences() {
    await this.page.goto('/sequences');
    await this.fastaTextArea.waitFor({ state: 'visible' });
  }

  async navigateAlignments() {
    await this.page.goto('/alignments');
    await this.calculateAlignmentButton.waitFor({ state: 'visible' });
  }

  async navigateClusters() {
    await this.page.goto('/clusters');
    await this.runClusteringButton.waitFor({ state: 'visible' });
  }

  async importFasta(fasta: string) {
    await this.fastaTextArea.fill(fasta);
    await this.runFastaImportButton.click();
    await this.page.waitForTimeout(2000);
  }

  async performPairwiseAlignment() {
    // Wait for dropdown options to load
    await expect(async () => {
      const count = await this.selectSeqA.locator('option').count();
      expect(count).toBeGreaterThanOrEqual(2);
    }).toPass({ timeout: 10000 });

    const options = await this.selectSeqA.locator('option').all();
    const valA = await options[0].getAttribute('value');
    const valB = await options[1].getAttribute('value');
    if (valA) await this.selectSeqA.selectOption(valA);
    if (valB) await this.selectSeqB.selectOption(valB);

    await this.calculateAlignmentButton.click();
    // Wait for calculation to complete and score to become visible
    await this.alignmentOutputScore.waitFor({ state: 'visible', timeout: 15000 });
  }
}
