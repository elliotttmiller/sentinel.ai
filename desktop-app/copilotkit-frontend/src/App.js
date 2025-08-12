import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Missions from "./pages/Missions";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";
import AgenticGenerativeUI from "./pages/AgenticGenerativeUI";
import CopilotChat from "./components/CopilotChat";
import NavBar from "./components/NavBar";
import SentinelInitializer from "./components/SentinelInitializer";
import Notification from "./components/Notification";
import { useNotification } from "./hooks/useNotification";

function App() {
  const { message, showNotification, clearNotification } = useNotification();
  // Optionally, pass showNotification to context for global use
  return (
    <div className="app-container">
      <SentinelInitializer />
      <Notification message={message} onClose={clearNotification} />
      <NavBar />
      {/* Global CopilotKit Chat Widget */}
      <CopilotChat />
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
