import React from 'react';
import SettingsForm from '../components/SettingsForm';
import './agentic-ui.css';

export default function SettingsPage() {
  return (
    <div className="agentic-ui-container">
      <h1>Settings</h1>
      <SettingsForm />
    </div>
  );
}
