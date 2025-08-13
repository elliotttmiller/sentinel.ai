import React, { useEffect } from "react";
import { TopBar } from "./components/TopBar";
import { AGUIBanner } from "./components/Banner";
import { TailoredContentProvider } from "./hooks/TailoredContentProvider.jsx";
import { useGoogleAnalytics } from "./hooks/useGoogleAnalytics";
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
  useGoogleAnalytics();
  return (
    <TailoredContentProvider>
      {/* CopilotKit is only for chat/agent operations. Apollo Client or similar should be used for GraphQL widgets. */}
      <CopilotKit
        runtimeUrl="http://127.0.0.1:8000/api/copilotkit"
        publicApiKey={process.env.REACT_APP_PUBLIC_API_KEY}
      >
        <div className="app-container">
          <TopBar />
          <AGUIBanner />
          <SentinelInitializer />
          <Notification message={message} onClose={clearNotification} />
          <NavBar />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/missions" element={<Missions />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </CopilotKit>
    </TailoredContentProvider>
  );
}

export default App;
