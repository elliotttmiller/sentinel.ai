import React from "react";
import "@copilotkit/react-ui/styles.css";
import "../styles/agentic.css";
// import { useCoAgent } from "@copilotkit/react-core";
import { CopilotChat, useCopilotChatSuggestions } from "@copilotkit/react-ui";

const initialPrompt = {
  agenticGenerativeUI: "Hi! I'm your agentic assistant. I will break down your request into actionable steps and keep you updated in real time. What would you like to do?"
};
const chatSuggestions = {
  agenticGenerativeUI: "Suggest tasks that can be broken down into steps, e.g., planning, multi-stage workflows, etc."
};


// AgenticSteps and agentic state rendering removed for compatibility

const Chat = () => {
  useCopilotChatSuggestions({
    instructions: chatSuggestions.agenticGenerativeUI,
  });

  return (
    <div className="flex justify-center items-center h-full w-full">
      <div className="w-8/10 h-8/10 rounded-lg">
        <CopilotChat
          className="h-full rounded-2xl"
          labels={{ initial: initialPrompt.agenticGenerativeUI }}
        />
      </div>
    </div>
  );
};

export default function AgenticGenerativeUI() {
  return <Chat />;
}
