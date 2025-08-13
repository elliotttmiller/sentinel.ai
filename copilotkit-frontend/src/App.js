import React, { useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Missions from "./pages/Missions";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";
import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-ui";
import { CopilotKit } from "@copilotkit/react-core";
// import { googleAdapter } from "./googleGenAIAdapter";
import CopilotAgent from "./components/CopilotAgent.jsx";
import NavBar from "./components/NavBar";
import SentinelInitializer from "./components/SentinelInitializer";
import Notification from "./components/Notification";
import { useNotification } from "./hooks/useNotification";

function App() {
  const { message, clearNotification } = useNotification();
  // Adapter registration is now handled by CopilotKit component. No need for CopilotRuntime or window.copilotKit.

  return (
    <CopilotKit runtimeUrl="http://127.0.0.1:8000/api/copilotkit">
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
        {/* AgenticGenerativeUI route removed; agentic generative UI is now integrated into main chat */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </CopilotKit>
  );
}

export default App;
