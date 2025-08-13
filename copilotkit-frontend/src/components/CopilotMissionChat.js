import React from "react";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import "../styles/copilotkit-chat-modern.css";

const observabilityHooks = {
  onMessageSent: (message) => {
    console.log("MissionChat: Message sent:", message);
  },
  onThumbsUp: (message) => {
    console.log("MissionChat: Thumbs up:", message);
  },
  onThumbsDown: (message) => {
    console.log("MissionChat: Thumbs down:", message);
  },
};

const renderError = (error) => (
  <div style={{ color: "red", padding: 8 }}>
    <b>Error:</b> {error.message}
    {error.operation && <span> ({error.operation})</span>}
    <button onClick={error.onDismiss} style={{ marginLeft: 8 }}>Dismiss</button>
    {error.onRetry && <button onClick={error.onRetry} style={{ marginLeft: 8 }}>Retry</button>}
  </div>
);

export default function CopilotMissionChat() {
  return (
    <CopilotChat
      labels={{
        title: "Mission Chat",
        initial: "Welcome to your mission chat.",
      }}
      observabilityHooks={observabilityHooks}
      renderError={renderError}
      className="copilot-chat-panel"
    />
  );
}
