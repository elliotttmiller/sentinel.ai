
import React, { useState } from 'react';
import Steps from '../components/Steps';
import AgentProgress from '../components/AgentProgress';
import './agentic-ui.css';

export default function AgenticUI() {
  const [task, setTask] = useState('');
  const [steps, setSteps] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSteps([]);
    setResult(null);

    // Connect to FastAPI streaming endpoint using EventSource (SSE)
    const eventSource = new EventSource(`/stream-agent-state?steps=${encodeURIComponent(task)}`);
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.observed_steps) {
          setSteps(data.observed_steps);
        }
      } catch (err) {
        // Ignore parse errors
      }
    };
    eventSource.onerror = () => {
      eventSource.close();
      setLoading(false);
      setResult('Streaming ended or error occurred.');
    };
    eventSource.addEventListener('end', () => {
      eventSource.close();
      setLoading(false);
    });
  };

  return (
    <div className="agentic-ui-container">
      <h1>Agentic Generative UI</h1>
      <form onSubmit={handleSubmit} className="agentic-ui-form">
        <input
          type="text"
          value={task}
          onChange={e => setTask(e.target.value)}
          placeholder="Enter comma-separated steps (e.g. step1,step2,step3)"
          className="agentic-ui-input"
        />
        <button type="submit" disabled={loading} className="agentic-ui-button">
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </form>
      <Steps />
      <AgentProgress steps={steps} />
      {result && <div className="agentic-ui-result">{result}</div>}
    </div>
  );
}
