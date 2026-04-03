import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',        // <-- your tests folder
  testMatch: ['*.spec.ts'],  // <-- match files ending with .spec.ts
  timeout: 60000,            // 60 seconds per test
  use: {
    headless: false,         // show browser if needed
    viewport: { width: 1280, height: 720 },
    actionTimeout: 30000,
  },
});