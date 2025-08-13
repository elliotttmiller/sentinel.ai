import React from "react";



import CopilotAgent from "../components/CopilotAgent.jsx";
import AgenticTaskExecutor from "../components/AgenticTaskExecutor";
import DashboardWidgets from "../components/DashboardWidgets";
import { DashboardContextProvider } from "../components/DashboardContextProvider";
import { DashboardActions } from "../components/DashboardActions";
import { OneOffTaskButton } from "../components/OneOffTaskButton";

import { HeadlessChatController } from "../components/HeadlessChatController";
function Dashboard() {
  return (
    <div style={{
      minHeight: "100vh",
      background: "#18181b",
      color: "#e5e7eb",
      fontFamily: "Inter, Arial, sans-serif",
      padding: 0,
    }}>
      <DashboardContextProvider />
      <DashboardActions />
      <header style={{
        padding: "2rem 2rem 1rem 2rem",
        background: "#232336",
        borderBottom: "1px solid #232336",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between"
      }}>
        <h1 style={{ fontSize: "2.5rem", fontWeight: 800, color: "#a5b4fc", letterSpacing: "-1px" }}>Sentinel Dashboard</h1>
        <span style={{ fontSize: "1.1rem", color: "#818cf8", fontWeight: 500 }}>CopilotKit Gemini 1.5 Pro</span>
      </header>
      <div style={{
        display: "flex",
        flexDirection: "row",
        gap: "2.5rem",
        padding: "2rem",
        maxWidth: "1600px",
        margin: "0 auto"
      }}>
        {/* Left: Main Agent Chat */}
        <div style={{
          flex: 1.2,
          background: "#232336",
          borderRadius: "1.5rem",
          boxShadow: "0 4px 24px rgba(40,40,60,0.18)",
          padding: "2rem",
          minWidth: "420px",
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch"
        }}>
          <CopilotAgent />
        </div>
        {/* Right: Task Executor & Widgets */}
        <div style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          gap: "2rem"
        }}>
          <AgenticTaskExecutor />
          <OneOffTaskButton />
          <HeadlessChatController />
          <div style={{
            background: "#232336",
            borderRadius: "1.5rem",
            boxShadow: "0 4px 24px rgba(40,40,60,0.18)",
            padding: "2rem"
          }}>
            <DashboardWidgets />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
