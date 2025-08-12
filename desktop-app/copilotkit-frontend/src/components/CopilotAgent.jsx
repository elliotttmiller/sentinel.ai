import React from "react";
import { CopilotProvider } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-chat";

const CopilotAgent = () => (
  <CopilotProvider>
    <CopilotChat
      title="Sentinel Copilot"
      placeholder="Ask Sentinel..."
      style={{ position: "fixed", bottom: 24, right: 24, zIndex: 1000 }}
    />
  </CopilotProvider>
);

export default CopilotAgent;
