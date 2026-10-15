import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import {
  acceptsSelection,
  assessmentStatus,
  payloadSchema,
  scoreLabel,
} from "../src/contracts";

const tokens: unknown = JSON.parse(
  readFileSync(
    new URL("../../../src/bond/data/design_tokens.json", import.meta.url),
    "utf8",
  ),
);

function examplePayload() {
  return {
    schema_version: 1,
    selected_service_id: "example_service",
    tokens,
    services: [{
      service: {
        id: "example_service",
        name: "Example Service",
        description: "Synthetic contract example.",
        owner: "Platform Engineering",
        tier: 1,
        dependencies: [],
        contract_visible: true,
        critical_vulnerabilities: null,
        observed_at: "2026-10-15T12:00:00Z",
        source: "synthetic",
      },
      results: [{
        rule_id: "contract_visible",
        version: "1",
        status: "pass",
        explanation: "Contract evidence is visible.",
      }],
      summary: { passed: 1, failed: 0, unknown: 1, total: 2 },
    }],
  };
}

test("payload parses the shared three tier tokens", () => {
  const payload = payloadSchema.parse(examplePayload());
  assert.equal(payload.tokens.primitives["canvas"], "#111216");
});

test("unknown initial service selection is rejected", () => {
  const payload = examplePayload();
  payload.selected_service_id = "not_present";
  assert.equal(payloadSchema.safeParse(payload).success, false);
});

test("selection outside the supplied view is rejected", () => {
  assert.equal(acceptsSelection({
    schema_version: 1,
    action: "inspect_service",
    service_id: "not_present",
    request_id: "00000000-0000-4000-8000-000000000001",
  }, new Set(["example_service"])), null);
});

test("extra message fields are rejected", () => {
  assert.equal(acceptsSelection({
    schema_version: 1,
    action: "inspect_service",
    service_id: "example_service",
    request_id: "00000000-0000-4000-8000-000000000001",
    override: true,
  }, new Set(["example_service"])), null);
});

test("missing evidence remains visible in status and score", () => {
  const payload = payloadSchema.parse(examplePayload());
  const assessment = payload.services[0];
  assert.ok(assessment);
  assert.equal(assessmentStatus(assessment), "unknown");
  assert.equal(scoreLabel(assessment), "50.0%");
});

test("duplicate service identifiers are rejected", () => {
  const payload = examplePayload();
  const first = payload.services[0];
  assert.ok(first);
  payload.services.push(first);
  assert.equal(payloadSchema.safeParse(payload).success, false);
});
