import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Missions from "./pages/Missions";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";
import AgenticGenerativeUI from "./pages/AgenticGenerativeUI";
import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-ui";
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
      {/* Official CopilotKit Chat Widget */}
      <CopilotChat
        instructions={"You are assisting the user as best as you can. Answer in the best way possible given the data you have."}
        labels={{
          title: "Your Assistant",
          initial: "Hi! 👋 How can I assist you today?",
        }}
      />
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
