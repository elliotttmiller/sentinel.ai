import React, { useEffect, useState } from "react";

function AnalyticsCharts() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/analytics")
      .then((res) => res.json())
      .then((data) => {
        setAnalytics(data);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading analytics...</div>;
  if (!analytics) return <div>No analytics data available.</div>;

  return (
    <div>
      <h2>System Analytics</h2>
      {/* Render analytics charts here, e.g., using recharts or chart.js */}
      <pre>{JSON.stringify(analytics, null, 2)}</pre>
    </div>
  );
}

export default AnalyticsCharts;
