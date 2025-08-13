import React from "react";
import { useCopilotChat } from "@copilotkit/react-core";
// ...existing code...

export default function AdvancedAgentPanel() {
  // Headless chat state
  const { visibleMessages, appendMessage } = useCopilotChat();

  // Agent state sharing removed: useCoAgent not available in this version

  // Streaming action removed: useCopilotAction not available in this version

  return (
    <div style={{ margin: "2rem 0" }}>
      <h2>Advanced Agent Panel</h2>
      {/* CopilotPopup removed: not compatible with React SPA */}
      <div style={{ color: 'gray', margin: '1rem 0' }}>[Agent popup feature coming soon]</div>
      <div style={{ marginTop: 16 }}>
        <strong>Agent State:</strong> {JSON.stringify(agentState)}
      </div>
      <div style={{ marginTop: 16 }}>
        <strong>Chat Messages:</strong>
        <ul>
          {visibleMessages.map((msg, i) => (
            <li key={i}><b>{msg.role}:</b> {msg.content}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
