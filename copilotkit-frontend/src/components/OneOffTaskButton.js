import { CopilotTask, useCopilotContext } from "@copilotkit/react-core";
import { useState } from "react";

export function OneOffTaskButton() {
  const context = useCopilotContext();
  const [message, setMessage] = useState("");

  const task = new CopilotTask({
    instructions: "Set a random message",
    actions: [
      {
        name: "setMessage",
        description: "Set the message.",
        argumentAnnotations: [
          {
            name: "message",
            type: "string",
            description: "A message to display.",
            required: true,
          },
        ],
      },
    ],
  });

  const executeTask = async () => {
    await task.run(context, { message: "Random message: " + Math.random() });
    setMessage("Random message set!");
  };

  return (
    <div style={{ marginTop: "2rem" }}>
      <button onClick={executeTask} style={{
        background: "#3730a3", color: "#fff", border: "none", borderRadius: "8px", padding: "0.75rem 1.5rem", fontWeight: 600, fontSize: "1rem", boxShadow: "0 2px 8px rgba(40,40,60,0.18)"
      }}>
        Execute One-Off Task
      </button>
      {message && <div style={{ marginTop: "1rem", color: "#a5b4fc" }}>{message}</div>}
    </div>
  );
}
