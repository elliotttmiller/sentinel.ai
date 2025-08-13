import { useCopilotChat } from "@copilotkit/react-core";
import { TextMessage, MessageRole } from "@copilotkit/runtime-client-gql";
import { useState } from "react";

export function HeadlessChatController() {
  const { appendMessage, isLoading, reset } = useCopilotChat();
  const [input, setInput] = useState("");

  const handleSendMessage = async () => {
    if (!input.trim()) return;
    await appendMessage(
      new TextMessage({
        role: MessageRole.User,
        content: input,
      })
    );
    setInput("");
  };

  return (
    <div style={{ marginTop: "2rem" }}>
      <input
        type="text"
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="Send a headless message..."
        style={{ width: 320, padding: 8, fontSize: 16, borderRadius: 8, border: "1px solid #3730a3", background: "#232336", color: "#e5e7eb" }}
      />
      <button
        onClick={handleSendMessage}
        disabled={isLoading}
        style={{ marginLeft: 8, background: "#3730a3", color: "#fff", border: "none", borderRadius: "8px", padding: "8px 16px", fontWeight: 600 }}
      >
        Send
      </button>
      <button
        onClick={reset}
        style={{ marginLeft: 8, background: "#232336", color: "#a5b4fc", border: "none", borderRadius: "8px", padding: "8px 16px", fontWeight: 600 }}
      >
        Reset
      </button>
    </div>
  );
}
