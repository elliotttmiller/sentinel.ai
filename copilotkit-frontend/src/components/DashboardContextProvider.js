import { useCopilotReadable } from "@copilotkit/react-core";
import { useState, useEffect } from "react";

export function DashboardContextProvider() {
  // Example dashboard stats
  const [stats, setStats] = useState({ users: 42, tasks: 17 });
  useCopilotReadable({
    description: "Dashboard statistics",
    value: stats,
  });
  // Simulate stats update
  useEffect(() => {
    const interval = setInterval(() => {
      setStats(s => ({ ...s, tasks: s.tasks + 1 }));
    }, 10000);
    return () => clearInterval(interval);
  }, []);
  return null;
}
