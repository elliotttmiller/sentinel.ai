import { useCopilotAction } from "@copilotkit/react-core";

export function DashboardActions() {
  useCopilotAction({
    name: "sayHello",
    description: "Say hello to someone.",
    parameters: [
      { name: "name", type: "string", description: "Name to greet" }
    ],
    handler: async ({ name }) => {
      alert(`Hello, ${name}!`);
    },
  });
  // Add more actions as needed
  return null;
}
