
import { CopilotProvider, useCopilotChat } from "@copilotkit/react-core";

function ChatBox() {
  const { visibleMessages, appendMessage } = useCopilotChat();
  const [input, setInput] = React.useState("");

  const handleSend = () => {
    if (input.trim()) {
      appendMessage({ role: "user", text: input });
      setInput("");
    }
  };

  return (
    <div style={{ position: "fixed", bottom: 24, right: 24, zIndex: 1000, background: "#fff", padding: 16, borderRadius: 8, boxShadow: "0 2px 8px rgba(0,0,0,0.15)" }}>
      <h3>Copilot Chat</h3>
      <div style={{ maxHeight: 200, overflowY: "auto", marginBottom: 8 }}>
        {visibleMessages.map((msg, idx) => (
          <div key={idx}><b>{msg.role}:</b> {msg.text}</div>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="Type your message..."
        style={{ width: "70%", marginRight: 8 }}
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}

const CopilotAgent = () => (
  <CopilotProvider>
    <ChatBox />
  </CopilotProvider>
);

export default CopilotAgent;
