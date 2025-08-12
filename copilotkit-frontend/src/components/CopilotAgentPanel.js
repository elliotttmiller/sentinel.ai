import React from "react";
import { CopilotAgent } from "@copilotkit/react";

function CopilotAgentPanel() {
  return (
    <div style={{ margin: "2rem 0" }}>
      <h2>Copilot Agent</h2>
      <CopilotAgent backendUrl="/api/llm/agent" />
    </div>
  );
}

export default CopilotAgentPanel;
