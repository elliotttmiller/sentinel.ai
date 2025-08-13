import React from "react";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import "../styles/copilotkit-chat-modern.css";
import "../styles/copilotkit-chat-dark.css";

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
    <div style={{
      width: "100%",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      minHeight: "800px",
      maxWidth: "1200px",
      margin: "0 auto",
      padding: "3rem 0"
    }}>
      <CopilotChat
        labels={{
          title: "Sentinel AI Agent",
          initial: "Hi! 👋 How can I assist you today? You can ask for complex tasks, analytics, or anything else.",
        }}
        instructions={"You are a highly advanced agent capable of executing complex generative tasks, analytics, and one-off actions. Integrate all agentic logic and respond with stepwise reasoning when needed."}
        suggestions={["Execute a complex mission", "Show analytics", "Run a one-off task", "Summarize system status"]}
        observabilityHooks={observabilityHooks}
        renderError={renderError}
        className="copilot-chat-panel"
        style={{ minHeight: "700px", fontSize: "1.25rem", width: "100%", boxShadow: "0 8px 32px rgba(40,40,60,0.22)", borderRadius: "2rem", background: "#232336" }}
      />
    </div>
  );
}
