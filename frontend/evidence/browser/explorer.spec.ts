import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

async function openCatalog(page: Page): Promise<void> {
  await page.goto("/?view=catalog");
  await expect(
    page.getByRole("heading", { name: "Catalog Repository", exact: true }),
  ).toBeVisible();
}

function explorer(page: Page) {
  return page.getByRole("region", {
    name: "Service evidence explorer",
    exact: true,
  });
}

async function enableSwitchByKeyboard(page: Page, name: string): Promise<void> {
  const control = page.getByRole("switch", { name, exact: true });
  await expect(control).not.toBeChecked();
  await control.focus();
  await expect(control).toBeFocused();
  await control.press("Space");
  await expect(control).toBeChecked();
}

test("the real React explorer renders without browser exceptions", async ({ page }) => {
  const failures: string[] = [];
  page.on("pageerror", error => failures.push(error.message));

  await openCatalog(page);
  await expect(explorer(page)).toBeVisible();
  await expect(
    explorer(page).getByRole("navigation", { name: "Choose a service" }),
  ).toBeVisible();

  await expect(
    explorer(page).getByRole("button", { name: /Billing Export/ }),
  ).toBeVisible();

  expect(failures).toEqual([]);
  await expect(page.getByTestId("stException")).toHaveCount(0);
});

test("keyboard selection and the Python inspection bridge work", async ({ page }) => {
  await openCatalog(page);

  const component = explorer(page);
  await expect(component).toBeVisible();

  const billing = component.getByRole("button", { name: /Billing Export/ });
  await billing.focus();
  await expect(billing).toBeFocused();
  await page.keyboard.press("Enter");

  const detail = component.getByRole("region", {
    name: "Billing Export",
    exact: true,
  });

  await expect(detail).toBeVisible();
  await expect(detail.getByText("Unassigned", { exact: true })).toBeVisible();
  await detail.getByRole("button", { name: "Inspect in catalog" }).click();

  const nativeSelector = page.getByTestId("stSelectbox").filter({
    hasText: "Inspect service",
  });

  const nativeInput = nativeSelector.getByRole("combobox", {
    name: "Inspect service",
    exact: true,
  });
  await expect(nativeInput).toHaveValue("Billing Export");
  await expect(page.getByTestId("stException")).toHaveCount(0);
});

test("native inspection remains available without the React explorer", async ({ page }) => {
  await openCatalog(page);
  await expect(explorer(page)).toBeVisible();

  await enableSwitchByKeyboard(page, "Use native evidence view");

  await expect(explorer(page)).toHaveCount(0);
  await expect(
    page.getByRole("heading", { name: "Native service inspection", exact: true }),
  ).toBeVisible();
  await expect(page.getByTestId("stException")).toHaveCount(0);

  await page.getByText("Use native evidence view", { exact: true }).click();
  await expect(
    page.getByRole("switch", {
      name: "Use native evidence view",
      exact: true,
    }),
  ).not.toBeChecked();
  await expect(explorer(page)).toBeVisible();
});

test("the narrow catalog stays within the viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openCatalog(page);
  await expect(explorer(page)).toBeVisible();

  const documentSize = await page.evaluate(() => ({
    scroll: document.documentElement.scrollWidth,
    viewport: window.innerWidth,
  }));

  expect(documentSize.scroll).toBeLessThanOrEqual(documentSize.viewport + 1);

  const componentSize = await explorer(page).evaluate(element => ({
    scroll: element.scrollWidth,
    width: element.clientWidth,
  }));

  expect(componentSize.scroll).toBeLessThanOrEqual(componentSize.width + 1);
});

test("the rendered evidence component passes its scoped accessibility scan", async ({ page }) => {
  await openCatalog(page);

  const component = explorer(page);
  await expect(component).toBeVisible();

  await component.evaluate(element => {
    const root = element.getRootNode();
    if (!(root instanceof ShadowRoot)) {
      throw new Error("Expected the component to use an isolated shadow root.");
    }
    root.host.setAttribute("data-bond-audit-host", "evidence");
  });

  const results = await new AxeBuilder({ page })
    .include([
      '[data-bond-audit-host="evidence"]',
      "#bond-evidence-root",
    ])
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
    .analyze();

  expect(
    results.violations.map(violation => ({
      id: violation.id,
      impact: violation.impact,
      description: violation.description,
      nodes: violation.nodes.map(node => ({
        target: node.target,
        summary: node.failureSummary,
      })),
    })),
  ).toEqual([]);
});

test("pipeline filtering changes the actual displayed sample set", async ({ page }) => {
  await page.goto("/?view=pipeline");
  await expect(
    page.getByRole("heading", { name: "Pipeline Laboratory", exact: true }),
  ).toBeVisible();

  await expect(
    page.getByText("Showing 10 of 10 query samples", { exact: true }),
  ).toBeVisible();

  await enableSwitchByKeyboard(
    page,
    "Show only samples above the review threshold",
  );

  await expect(
    page.getByText("Showing 2 of 10 query samples", { exact: true }),
  ).toBeVisible();

  await expect(page.getByTestId("stException")).toHaveCount(0);
  await expect(
    page.getByText("Exploratory filter only.", { exact: false }),
  ).toBeVisible();
});
