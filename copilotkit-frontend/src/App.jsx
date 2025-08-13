import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./views/Dashboard";
import Missions from "./views/Missions";
import Analytics from "./views/Analytics";
import Settings from "./views/Settings";
import TestMissions from "./views/TestMissions";
import CopilotAgent from "./components/CopilotAgent";
import "./styles/global.css";

function App() {
  return (
    <Router>
      <CopilotAgent />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/missions" element={<Missions />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/test-missions" element={<TestMissions />} />
      </Routes>
    </Router>
  );
}

export default App;
