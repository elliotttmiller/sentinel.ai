import React from "react";
import { CopilotChat } from "@copilotkit/react-chat";

function CopilotChatWidget() {
  return (
    <CopilotChat
      backendUrl="/api/llm/chat" // Proxy to Flask backend for Gemini LLM
      title="Sentinel Copilot"
      placeholder="Ask Sentinel anything..."
      theme="auto"
    />
  );
}

export default CopilotChatWidget;
