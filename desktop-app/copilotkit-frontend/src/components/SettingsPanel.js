import React, { useEffect, useState } from "react";

function SettingsPanel() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/settings")
      .then((res) => res.json())
      .then((data) => {
        setSettings(data);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading settings...</div>;
  if (!settings) return <div>No settings data available.</div>;

  return (
    <div>
      <h2>System Settings</h2>
      <pre>{JSON.stringify(settings, null, 2)}</pre>
      {/* Add forms for updating settings here */}
    </div>
  );
}

export default SettingsPanel;
