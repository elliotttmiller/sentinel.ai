import React, { useEffect, useState } from 'react';

export default function AgentProgress({ steps }: { steps: string[] }) {
  return (
    <div className="agentic-ui-progress">
      <h2>Agent Progress</h2>
      <ol>
        {steps.map((step, idx) => (
          <li key={idx} className="agentic-ui-step">{step}</li>
        ))}
      </ol>
    </div>
  );
}
