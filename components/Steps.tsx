import React from 'react';
import './agentic-ui.css';

const steps = [
  'Enter your task/request',
  'Submit to Gemini agent',
  'View agent response',
];

export default function Steps() {
  return (
    <div className="agentic-ui-steps">
      <h2>Workflow Steps</h2>
      <ol>
        {steps.map((step, idx) => (
          <li key={idx} className="agentic-ui-step">{step}</li>
        ))}
      </ol>
    </div>
  );
}
