import React, { useState, useEffect } from "react";
import { useCopilotReadable, useCopilotAdditionalInstructions, useCopilotChat, useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { useCopilotChatSuggestions } from "@copilotkit/react-ui";
import { TextMessage, MessageRole } from "@copilotkit/runtime-client-gql";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./views/Dashboard";
import Missions from "./views/Missions";
import Analytics from "./views/Analytics";
import Settings from "./views/Settings";
import TestMissions from "./views/TestMissions";
import CopilotAgent from "./components/CopilotAgent";
import "./styles/global.css";

function App() {
  // Sample todo list state for Copilot actions
  const [todos, setTodos] = useState([]);

  // Define Copilot action to add todo items
  useCopilotAction({
    name: "addTodoItem",
    description: "Add a new todo item to the list",
    parameters: [
      {
        name: "todoText",
        type: "string",
        description: "The text of the todo item to add",
        required: true,
      },
    ],
    handler: async ({ todoText }) => {
      setTodos([...todos, todoText]);
    },
    available: "enabled"
  });
  // Provide additional instructions to Copilot globally
  useCopilotAdditionalInstructions({
    instructions: "Do not answer questions about the weather. Do not answer questions about the stock market.",
    available: "enabled"
  });

  // Integrate useCopilotChat globally
  const { appendMessage, isLoading, reset, runChatCompletion } = useCopilotChat();

  // Example: Programmatically send a message to Copilot
  const sendCopilotMessage = async (content) => {
    await appendMessage(
      new TextMessage({
        role: MessageRole.User,
        content,
      })
    );
  };

  // Integrate useCopilotChatSuggestions globally
  useCopilotChatSuggestions({
    instructions: `Suggest relevant actions for the current route: ${currentRoute}`,
    minSuggestions: 1,
    maxSuggestions: 3,
    available: "enabled"
  }, [currentRoute]);

  // Agent state rendering now handled directly via useCoAgent below

  // Integrate useCoAgent globally with a sample counter state
  const agent = useCoAgent({
    name: "my-agent",
    initialState: { count: 0 },
  });

  // Example UI for bidirectional state sharing
  // This can be moved to a dedicated component if needed
  const { state, setState } = agent;
  // Example: Track current route for Copilot context
  const [currentRoute, setCurrentRoute] = useState(window.location.pathname);

  useEffect(() => {
    const handleRouteChange = () => setCurrentRoute(window.location.pathname);
    window.addEventListener("popstate", handleRouteChange);
    return () => window.removeEventListener("popstate", handleRouteChange);
  }, []);

  useCopilotReadable({
    description: "Current route in the application",
    value: currentRoute,
    categories: ["navigation", "global"],
    available: "enabled"
  });

  return (
    <>
      <div style={{ padding: "8px", background: "#e3f2fd", borderRadius: "4px", margin: "8px 0" }}>
        <strong>CoAgent Counter Demo:</strong><br />
        Count: {state.count}
        <button style={{ marginLeft: "8px" }} onClick={() => setState({ count: state.count + 1 })}>Increment</button>
      </div>
      <div style={{ padding: "8px", background: "#fffde7", borderRadius: "4px", margin: "8px 0" }}>
        <strong>Copilot Todo List:</strong>
        <ul>
          {todos.map((todo, index) => (
            <li key={index}>{todo}</li>
          ))}
        </ul>
      </div>
      <Router>
        <CopilotAgent />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/missions" element={<Missions />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/test-missions" element={<TestMissions />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;
