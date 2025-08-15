import React from 'react';
import HistoryList from '../components/HistoryList';
import './agentic-ui.css';

export default function HistoryPage() {
  return (
    <div className="agentic-ui-container">
      <h1>History</h1>
      <HistoryList />
    </div>
  );
}
