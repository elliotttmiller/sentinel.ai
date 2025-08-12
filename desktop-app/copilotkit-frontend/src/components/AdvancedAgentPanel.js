import React from "react";
import { useCopilotChat, useCopilotAction, useCoAgent } from "@copilotkit/react-core";
import { CopilotPopup } from "@copilotkit/react-ui";

export default function AdvancedAgentPanel() {
  // Headless chat state
  const { visibleMessages, appendMessage } = useCopilotChat();

  // Example: Agent state sharing (LangGraph/CrewAI compatible)
  const { agentState } = useCoAgent({ name: "sentinel_agent", initialState: { input: "Ready" } });

  // Example: Streaming action with custom render
  useCopilotAction({
    name: "appendToMissionLog",
    description: "Append entries to the current mission log",
    parameters: [
      { name: "entries", type: "object[]", attributes: [{ name: "text", type: "string" }] }
    ],
    render: ({ status, args }) => (
      <div>
        <h4>Mission Log Streaming</h4>
        {args.entries && args.entries.map((e, i) => <div key={i}>{e.text}</div>)}
        <div>Status: {status}</div>
      </div>
    ),
    handler: ({ entries }) => {
      // Custom logic to update mission log in your backend or state
      // For demo, just append to chat
      entries.forEach(e => appendMessage({ role: "assistant", content: e.text }));
    },
  });

  return (
    <div style={{ margin: "2rem 0" }}>
      <h2>Advanced Agent Panel</h2>
      <CopilotPopup
        instructions={"You are Sentinel's advanced AI agent. Help the user with mission control, analytics, and troubleshooting."}
        labels={{ title: "Sentinel Agent", initial: "How can I assist you?" }}
      />
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
