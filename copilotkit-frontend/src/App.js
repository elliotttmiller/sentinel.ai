import React from "react";
import { Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Missions from "./pages/Missions";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";
import AgenticGenerativeUI from "./pages/AgenticGenerativeUI";
import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-ui";
import CopilotAgent from "./components/CopilotAgent.jsx";
import NavBar from "./components/NavBar";
import SentinelInitializer from "./components/SentinelInitializer";
import Notification from "./components/Notification";
import { useNotification } from "./hooks/useNotification";

function App() {
  const { message, clearNotification } = useNotification();
  // Optionally, pass showNotification to context for global use
  // Custom CopilotKit network override
  const customSendMessage = async (messages) => {
    // Always send correct payload format
    const formattedMessages = Array.isArray(messages)
      ? messages.map(msg => (typeof msg === 'string' ? { text: msg } : msg))
      : [{ text: String(messages) }];
    const response = await fetch("/copilotkit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: formattedMessages }),
    });
    if (!response.ok) throw new Error("CopilotKit request failed");
    return response.json();
  };

  return (
    <div className="app-container">
      <SentinelInitializer />
      <Notification message={message} onClose={clearNotification} />
      <NavBar />
      {/* Custom CopilotKit Chat Widget using guaranteed payload utility */}
      <CopilotAgent />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/missions" element={<Missions />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/agentic-generative-ui" element={<AgenticGenerativeUI />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  );
}

export default App;
