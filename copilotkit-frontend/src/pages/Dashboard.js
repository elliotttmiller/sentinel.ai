import React from "react";



import CopilotAgent from "../components/CopilotAgent.jsx";
import DashboardWidgets from "../components/DashboardWidgets";
import { DashboardContextProvider } from "../components/DashboardContextProvider";
import { DashboardActions } from "../components/DashboardActions";
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
        padding: "2rem 0",
        maxWidth: "1600px",
        margin: "0 auto"
      }}>
        {/* Main Chat Panel - visually dominant and centered */}
        <div style={{
          flex: 2.5,
          background: "#18181b",
          borderRadius: "2rem",
          boxShadow: "0 8px 32px rgba(40,40,60,0.22)",
          padding: "3.5rem 2.5rem",
          minWidth: "800px",
          maxWidth: "1200px",
          margin: "0 auto",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center"
        }}>
          <CopilotAgent />
        </div>
        {/* Sidebar Widgets */}
        <div style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          gap: "2rem",
          minWidth: "320px"
        }}>
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
