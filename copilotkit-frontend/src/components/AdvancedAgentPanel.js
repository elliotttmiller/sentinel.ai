export default function AdvancedAgentPanel() {
  // Observability hooks for debugging and analytics
  const observabilityHooks = {
    onMessageSent: (message) => {
      console.log("AdvancedAgentPanel: Message sent:", message);
    },
    onThumbsUp: (message) => {
      console.log("AdvancedAgentPanel: Thumbs up:", message);
    },
    onThumbsDown: (message) => {
      console.log("AdvancedAgentPanel: Thumbs down:", message);
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

  return (
    <div className="advanced-agent-panel">
      <h2 style={{fontSize: "2rem", fontWeight: 700, marginBottom: "1.5rem", color: "#3730a3"}}>Advanced Agent Panel</h2>
      <CopilotChat
        labels={{
          title: "Agent Chat",
          initial: "Welcome to the advanced agent panel.",
        }}
        observabilityHooks={observabilityHooks}
        renderError={renderError}
        className="advanced-agent-panel"
      />
    </div>
  );
}
