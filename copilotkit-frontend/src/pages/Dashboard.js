import React from "react";


import DashboardWidgets from "../components/DashboardWidgets";

import CopilotAgentPanel from "../components/CopilotAgentPanel";
import AdvancedAgentPanel from "../components/AdvancedAgentPanel";
import AgenticTaskExecutor from "../components/AgenticTaskExecutor";

function Dashboard() {
  return (
    <div>
      <h1>Sentinel Dashboard</h1>
      <DashboardWidgets />
      <CopilotAgentPanel />
      <AdvancedAgentPanel />
      <AgenticTaskExecutor />
    </div>
  );
}

export default Dashboard;
