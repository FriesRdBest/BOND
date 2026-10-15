import { z } from "zod";

const identifier = z.string().regex(/^[a-z][a-z0-9_]{2,63}$/);
const tokenName = z.string().regex(/^[a-z_]+$/);
const status = z.enum(["pass", "fail", "unknown"]);

export const selectionSchema = z.object({
  schema_version: z.literal(1),
  action: z.literal("inspect_service"),
  service_id: identifier,
  request_id: z.uuid(),
}).strict();

const serviceSchema = z.object({
  id: identifier,
  name: z.string().min(1).max(160),
  description: z.string().min(1).max(160),
  owner: z.string().min(1).max(160).nullable(),
  tier: z.number().int().min(1).max(3),
  dependencies: z.array(identifier),
  contract_visible: z.boolean().nullable(),
  critical_vulnerabilities: z.number().int().nonnegative().nullable(),
  observed_at: z.string().datetime({ offset: true }),
  source: z.literal("synthetic"),
}).strict();

const resultSchema = z.object({
  rule_id: identifier,
  version: z.string(),
  status,
  explanation: z.string().min(1).max(160),
}).strict();

const summarySchema = z.object({
  passed: z.number().int().nonnegative(),
  failed: z.number().int().nonnegative(),
  unknown: z.number().int().nonnegative(),
  total: z.number().int().nonnegative(),
}).strict().refine(
  value => value.passed + value.failed + value.unknown === value.total,
  { message: "Rule counts must match the total." },
);

const assessmentSchema = z.object({
  service: serviceSchema,
  results: z.array(resultSchema),
  summary: summarySchema,
}).strict();

const tokensSchema = z.object({
  primitives: z.record(tokenName, z.string().min(1).max(300)),
  semantic: z.record(tokenName, tokenName),
  components: z.record(tokenName, tokenName),
}).strict();

export const payloadSchema = z.object({
  schema_version: z.literal(1),
  selected_service_id: identifier.nullable(),
  services: z.array(assessmentSchema).max(200),
  tokens: tokensSchema,
}).strict().superRefine((value, context) => {
  const ids = new Set(value.services.map(item => item.service.id));

  if (ids.size !== value.services.length) {
    context.addIssue({ code: "custom", message: "Service identifiers must be unique." });
  }

  if (value.selected_service_id !== null && !ids.has(value.selected_service_id)) {
    context.addIssue({ code: "custom", message: "The selected service is unknown." });
  }

  for (const reference of Object.values(value.tokens.semantic)) {
    if (!(reference in value.tokens.primitives)) {
      context.addIssue({ code: "custom", message: "Unknown primitive token." });
    }
  }

  for (const reference of Object.values(value.tokens.components)) {
    if (!(reference in value.tokens.semantic)) {
      context.addIssue({ code: "custom", message: "Unknown semantic token." });
    }
  }
});

export type ExplorerPayload = z.infer<typeof payloadSchema>;
export type Assessment = ExplorerPayload["services"][number];
export type SelectionMessage = z.infer<typeof selectionSchema>;

export function acceptsSelection(
  input: unknown,
  allowedIds: ReadonlySet<string>,
): SelectionMessage | null {
  const parsed = selectionSchema.safeParse(input);
  if (!parsed.success || !allowedIds.has(parsed.data.service_id)) {
    return null;
  }
  return parsed.data;
}

export function assessmentStatus(assessment: Assessment): "pass" | "fail" | "unknown" {
  if (assessment.summary.failed > 0) return "fail";
  if (assessment.summary.unknown > 0 || assessment.summary.total === 0) return "unknown";
  return "pass";
}

export function scoreLabel(assessment: Assessment): string {
  const { passed, total } = assessment.summary;
  return total === 0 ? "No score" : `${((passed / total) * 100).toFixed(1)}%`;
}
