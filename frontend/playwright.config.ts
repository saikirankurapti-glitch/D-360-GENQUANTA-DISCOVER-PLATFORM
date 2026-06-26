import { defineConfig, devices } from '@playwright/test';
import path from 'path';

export default defineConfig({
  testDir: './tests',
  timeout: 180000,
  fullyParallel: false, // Run sequentially to avoid database conflicts
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1, // Single worker to ensure sequential database operations
  reporter: [['html', { open: 'never' }], ['list']],
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'on',
    video: 'on',
    viewport: { width: 1280, height: 800 },
  },
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: ['--disable-gpu']
        }
      },
    },
  ],
});
