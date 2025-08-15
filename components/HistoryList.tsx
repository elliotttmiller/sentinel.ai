import React from 'react';
import './agentic-ui.css';

const demoHistory = [
  { id: 1, task: 'Summarize this document', result: 'Demo summary result.' },
  { id: 2, task: 'Generate a travel plan', result: 'Demo travel plan result.' },
];

export default function HistoryList() {
  return (
    <div className="history-list">
      <h2>Past Results</h2>
      <ul>
        {demoHistory.map(item => (
          <li key={item.id} className="history-item">
            <strong>Task:</strong> {item.task}<br />
            <strong>Result:</strong> {item.result}
          </li>
        ))}
      </ul>
    </div>
  );
}
