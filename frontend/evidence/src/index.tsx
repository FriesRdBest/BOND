import type { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import { createRoot } from "react-dom/client";
import { Explorer } from "./Explorer";
import { payloadSchema } from "./contracts";
import "bond:tokens";
import "./styles.css";

export default function render(component: FrontendRendererArgs): () => void {
  const mount = component.parentElement.querySelector("#bond-evidence-root");

  if (!(mount instanceof HTMLElement)) {
    throw new Error("BOND evidence mount is unavailable.");
  }

  const root = createRoot(mount);
  const parsed = payloadSchema.safeParse(component.data);

  if (!parsed.success) {
    root.render(
      <section className="bond-explorer" role="alert">
        <h3>Evidence could not be displayed</h3>
        <p>Use the native catalog inspection below. No action was performed.</p>
      </section>,
    );
  } else {
    root.render(
      <Explorer
        payload={parsed.data}
        onInspect={message => component.setStateValue("selection", message)}
      />,
    );
  }

  return () => root.unmount();
}
