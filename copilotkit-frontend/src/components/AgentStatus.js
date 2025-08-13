import React from "react";
import { useWebSocketStatus } from "../hooks/useWebSocketStatus";

export default function AgentStatus() {
  const status = useWebSocketStatus();
  return (
    <div>
      <h3>Agent Status (WebSocket)</h3>
      <div>{status}</div>
    </div>
  );
}
