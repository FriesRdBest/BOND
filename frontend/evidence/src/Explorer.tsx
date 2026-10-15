import { useState } from "react";
import {
  assessmentStatus,
  scoreLabel,
  type ExplorerPayload,
  type SelectionMessage,
} from "./contracts";

interface ExplorerProps {
  payload: ExplorerPayload;
  onInspect: (message: SelectionMessage) => void;
}

const labels = {
  pass: "Passing",
  fail: "Needs attention",
  unknown: "Missing evidence",
} as const;

export function Explorer({ payload, onInspect }: ExplorerProps) {
  const [selectedId, setSelectedId] = useState(
    payload.selected_service_id ?? payload.services[0]?.service.id ?? null,
  );

  const selected = payload.services.find(item => item.service.id === selectedId)
    ?? payload.services[0];

  if (!selected) {
    return (
      <section className="bond-explorer" aria-label="Service evidence explorer">
        <div className="empty-state" role="status">
          <h3>No services in this view</h3>
          <p>Change the catalog filters to inspect another service.</p>
        </div>
      </section>
    );
  }

  const selectedStatus = assessmentStatus(selected);

  return (
    <section className="bond-explorer" aria-label="Service evidence explorer">
      <header className="explorer-header">
        <div>
          <p className="eyebrow">Evidence explorer</p>
          <h3>From service context to a clear finding</h3>
        </div>
        <span className="source-label">Synthetic evidence</span>
      </header>

      <div className="explorer-layout">
        <nav className="service-list" aria-label="Choose a service">
          {payload.services.map(item => {
            const state = assessmentStatus(item);
            const active = item.service.id === selected.service.id;

            return (
              <button
                key={item.service.id}
                type="button"
                className={`service-option ${active ? "is-selected" : ""}`}
                aria-pressed={active}
                onClick={() => setSelectedId(item.service.id)}
              >
                <span className="option-heading">
                  <span>{item.service.name}</span>
                  <span className="score">{scoreLabel(item)}</span>
                </span>
                <span className="option-owner">{item.service.owner ?? "Unassigned"}</span>
                <span className={`status status-${state}`}>{labels[state]}</span>
              </button>
            );
          })}
        </nav>

        <section className="evidence-detail" aria-labelledby="bond-evidence-title">
          <div className="detail-heading">
            <div>
              <p className="eyebrow">Service evidence</p>
              <h3 id="bond-evidence-title">{selected.service.name}</h3>
            </div>
            <span className={`status status-${selectedStatus}`}>
              {labels[selectedStatus]}
            </span>
          </div>

          <p className="description">{selected.service.description}</p>

          <dl className="facts">
            <div><dt>Accountable owner</dt><dd>{selected.service.owner ?? "Unassigned"}</dd></div>
            <div><dt>Service tier</dt><dd>{selected.service.tier}</dd></div>
            <div><dt>Maturity</dt><dd>{scoreLabel(selected)}</dd></div>
          </dl>

          <div className="rules" aria-label="Rule evidence">
            {selected.results.map(rule => (
              <article key={rule.rule_id} className="rule-card">
                <div className="rule-heading">
                  <span className={`status status-${rule.status}`}>
                    {rule.status === "pass" ? "Pass" : labels[rule.status]}
                  </span>
                  <span className="rule-version">Version {rule.version}</span>
                </div>
                <p>{rule.explanation}</p>
                <code>{rule.rule_id}</code>
              </article>
            ))}
          </div>

          <div className="dependency-context">
            <h4>Dependency context</h4>
            <p>
              {selected.service.dependencies.length > 0
                ? selected.service.dependencies.join(", ")
                : "No dependencies recorded"}
            </p>
          </div>

          <footer className="detail-footer">
            <p>
              Fixed observation<br />
              <time dateTime={selected.service.observed_at}>
                {selected.service.observed_at}
              </time>
            </p>
            <button
              type="button"
              className="inspect-button"
              onClick={() => onInspect({
                schema_version: 1,
                action: "inspect_service",
                service_id: selected.service.id,
                request_id: crypto.randomUUID(),
              })}
            >
              Inspect in catalog
            </button>
          </footer>

          <p className="selection-announcement" role="status" aria-live="polite">
            Selected service: {selected.service.name}
          </p>
        </section>
      </div>
    </section>
  );
}
