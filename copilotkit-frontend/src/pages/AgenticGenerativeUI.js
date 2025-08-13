import React from "react";
// ...existing code...
import "../styles/agentic.css";
import { CopilotProvider } from "@copilotkit/react-core";
import { useCoAgentStateRender } from "@copilotkit/react-ui";
import CopilotChat from "../components/CopilotChat";

const AGENT_NAME = "agentic_generative_ui";
const RUNTIME_URL = "https://sentinelai-production.up.railway.app/api/copilotkit";

function Spinner() {
  return (
    <svg className="mr-2 size-3 animate-spin text-slate-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
  );
}

const AgenticSteps = ({ steps }) => {
  if (!steps || steps.length === 0) return null;
  const firstPending = steps.findIndex((s) => s.status === "pending");
  return (
    <div className="flex">
      <div className="bg-gray-100 rounded-lg w-[500px] p-4 text-black space-y-2">
        {steps.map((step, index) => {
          if (step.status === "completed") {
            return (
              <div key={index} className="text-sm">✓ {step.description}</div>
            );
          } else if (step.status === "pending" && index === firstPending) {
            return (
              <div key={index} className="text-3xl font-bold text-slate-700">
                <Spinner /> {step.description}
              </div>
            );
          } else {
            return (
              <div key={index} className="text-sm">
                <Spinner /> {step.description}
              </div>
            );
          }
        })}
      </div>
    </div>
  );
};

const Chat = () => {
  // useCopilotChatSuggestions removed: not compatible with React SPA
  useCoAgentStateRender({
    name: AGENT_NAME,
    render: ({ state }) => <AgenticSteps steps={state.steps} />,
  });
  return (
    <div className="flex justify-center items-center h-full w-full">
      <div className="w-8/10 h-8/10 rounded-lg">
        <CopilotChat />
      </div>
    </div>
  );
};

export default function AgenticGenerativeUI() {
  const publicApiKey = process.env.REACT_APP_PUBLIC_API_KEY;
  return (
    <CopilotProvider
      runtimeUrl={RUNTIME_URL}
      showDevConsole={false}
      agent={AGENT_NAME}
      publicApiKey={publicApiKey}
    >
      <Chat />
    </CopilotProvider>
  );
}
