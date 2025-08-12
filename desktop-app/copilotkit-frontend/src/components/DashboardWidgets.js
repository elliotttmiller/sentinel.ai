import React, { useEffect, useState } from "react";

function DashboardWidgets() {
  const [widgets, setWidgets] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/dashboard")
      .then((res) => res.json())
      .then((data) => {
        setWidgets(data);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading dashboard...</div>;
  if (!widgets) return <div>No dashboard data available.</div>;

  return (
    <div>
      <h2>System Overview</h2>
      <pre>{JSON.stringify(widgets, null, 2)}</pre>
      {/* Add more widgets and CopilotKit-powered insights here */}
    </div>
  );
}

export default DashboardWidgets;
