import React from "react";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import "../styles/copilotkit-chat-modern.css";

// Observability hooks for debugging and analytics
const observabilityHooks = {
  onMessageSent: (message) => {
    console.log("Message sent:", message);
  },
  onThumbsUp: (message) => {
    console.log("Thumbs up:", message);
  },
  onThumbsDown: (message) => {
    console.log("Thumbs down:", message);
  },
};

// Custom error renderer
const renderError = (error) => (
  <div style={{ color: "red", padding: 8 }}>
    <b>Error:</b> {error.message}
    {error.operation && <span> ({error.operation})</span>}
    <button onClick={error.onDismiss} style={{ marginLeft: 8 }}>Dismiss</button>
    {error.onRetry && <button onClick={error.onRetry} style={{ marginLeft: 8 }}>Retry</button>}
  </div>
);

export default function CopilotAgent() {
  return (
    <CopilotChat
      labels={{
        title: "Your Assistant",
        initial: "Hi! 👋 How can I assist you today?",
      }}
      observabilityHooks={observabilityHooks}
      renderError={renderError}
      className="copilot-chat-panel"
    />
  );
}
