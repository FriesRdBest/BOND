import { expect, test } from "@playwright/test";

test("the catalog completes a simulated assurance workflow", async ({ page }) => {
  await page.goto("/?view=catalog");
  await expect(page.getByRole("heading", { name: "Catalog Repository" })).toBeVisible();

  await page
    .getByRole("button", { name: /^Billing Export 33\.3%/ })
    .click();

  await page.getByRole("button", { name: "Inspect in catalog" }).click();

  await expect(async () => {
    await expect(page.getByLabel("Evidence finding")).toBeVisible();
  }).toPass({ timeout: 30_000 });

  await expect(
    page.getByRole("heading", { name: "Improvement workflow" }),
  ).toBeVisible();
  await expect(
    page.getByLabel("Recommendation title"),
  ).toHaveValue("Address ownership_assigned for Billing Export");

  await page
    .getByLabel("Recommendation title")
    .fill("Assign an accountable Billing Export owner");
  await page
    .getByLabel("Why this action is recommended")
    .fill("No accountable owner is assigned to this service.");
  await page
    .getByLabel("Expected verified result")
    .fill("An accountable owner is assigned in the evidence.");

  await page.getByRole("button", { name: "Propose recommendation" }).click();

  const approve = page.getByRole("button", { name: "Approve" });
  await expect(approve).toBeVisible();
  await approve.click();

  const execute = page.getByRole("button", {
    name: "Record simulated execution",
  });
  await expect(execute).toBeVisible();
  await execute.click();

  const verify = page.getByRole("button", { name: "Verify success" });
  await expect(verify).toBeVisible();
  await verify.click();

  await expect(page.getByText("Verified")).toBeVisible();

  await page.getByText("Audit history").click();

  await expect(page.getByText("recommendation_created").first()).toBeAttached();
  await expect(page.getByText("approval_granted").first()).toBeAttached();
  await expect(page.getByText("simulated_execution_recorded").first()).toBeAttached();
  await expect(page.getByText("verification_passed").first()).toBeAttached();
});
