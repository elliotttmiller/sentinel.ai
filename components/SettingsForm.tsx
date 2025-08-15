import React, { useState } from 'react';
import './agentic-ui.css';

export default function SettingsForm() {
  const [apiKey, setApiKey] = useState('');
  const [agentName, setAgentName] = useState('Gemini');

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Save API key and agent config securely
    alert('Settings saved (demo only).');
  };

  return (
    <form onSubmit={handleSave} className="settings-form">
      <label>
        Google API Key:
        <input
          type="text"
          value={apiKey}
          onChange={e => setApiKey(e.target.value)}
          className="settings-input"
        />
      </label>
      <label>
        Agent Name:
        <input
          type="text"
          value={agentName}
          onChange={e => setAgentName(e.target.value)}
          className="settings-input"
        />
      </label>
      <button type="submit" className="settings-save-btn">Save</button>
    </form>
  );
}
