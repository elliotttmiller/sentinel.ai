import React, { useState } from 'react';
import './agentic-ui.css';

export default function ChatWindow() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setMessages([...messages, { role: 'user', content: input }]);
    // TODO: Connect to backend API for agent response
    setTimeout(() => {
      setMessages(msgs => [...msgs, { role: 'agent', content: 'Demo: Gemini agent response.' }]);
      setLoading(false);
    }, 1200);
    setInput('');
  };

  return (
    <div className="chat-window">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message chat-message-${msg.role}`}>
            <span>{msg.content}</span>
          </div>
        ))}
      </div>
      <form onSubmit={handleSend} className="chat-form">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Type your message..."
          className="chat-input"
        />
        <button type="submit" disabled={loading} className="chat-send-btn">
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}
