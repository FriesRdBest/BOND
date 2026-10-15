import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./browser",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  maxFailures: 1,
  timeout: 45_000,
  expect: { timeout: 20_000 },
  reporter: [["list"]],
  outputDir: "../../.artifacts/browser",
  use: {
    baseURL: "http://127.0.0.1:8511",
    browserName: "chromium",
    headless: true,
    viewport: { width: 1440, height: 1000 },
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  webServer: {
    command:
      "cd ../.. && .venv/bin/python -m streamlit run app.py " +
      "--server.address=127.0.0.1 --server.port=8511 --server.headless=true " +
      "--browser.gatherUsageStats=false",
    url: "http://127.0.0.1:8511/_stcore/health",
    reuseExistingServer: false,
    timeout: 60_000,
    stdout: "ignore",
    stderr: "pipe",
  },
});
