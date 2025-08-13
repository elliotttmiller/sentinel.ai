import React from "react";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import "../styles/copilotkit-chat-modern.css";

const observabilityHooks = {
  onMessageSent: (message) => {
    console.log("ChatWidget: Message sent:", message);
  },
  onThumbsUp: (message) => {
    console.log("ChatWidget: Thumbs up:", message);
  },
  onThumbsDown: (message) => {
    console.log("ChatWidget: Thumbs down:", message);
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

export default function CopilotChatWidget() {
  return (
    <CopilotChat
      labels={{
        title: "Chat Widget",
        initial: "Welcome to the chat widget.",
      }}
      observabilityHooks={observabilityHooks}
      renderError={renderError}
      className="copilot-chat-panel"
    />
  );
}
